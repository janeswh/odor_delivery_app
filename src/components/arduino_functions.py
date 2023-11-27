"""Contains the ArduinoSession class to communicate with the Arduino board
and display experiment progress."""

import flet as ft
from flet import UserControl, Column, Container, Text, TextField, Row

import datetime
import serial
import pdb
import time
import pandas as pd
import os

from threading import Thread, Event


class ArduinoSession(UserControl):
    """Controls communication with the Arduino board and contains layout
    displaying experimental progress."""

    def __init__(
        self,
        panel_type: str,
        csv_time: str,
        page: ft.Page,
        settings: dict,
        odor_sequence: list,
    ):
        """Initializes an instance for holding signals sent to the arduino per
        session.

        Args:
            panel_type: Whether odor panel is 1% or 10%.
            csv_time: Timestamp for saving the csv file.
            page: The page that OdorDeliveryApp will be added to.
            settings: All experiment settings entered from settings fields.
            odor_sequence: The order of odor delivery, by odor number.
        """

        super().__init__()

        #: str: Whether odor panel is 1% or 10%
        self.panel_type = panel_type

        #: str: Timestamp for saving the csv file
        self.csv_time = csv_time

        #: ft.Page: The page that OdorDeliveryApp will be added to
        self.page = page

        #: dict: All experiment settings entered from settings fields
        self.acq_params = settings

        #: list: The order of odor delivery, by odor (solenoid) number
        self.solenoid_order = odor_sequence

        #: str: The date of the experiment
        self.date = settings["date"]

        #: str: The animal ID of the experiment
        self.animal_id = settings["mouse"]

        #: roi: The ROI of the experiment
        self.roi = settings["roi"]

        #: str: The directory for saving solenoid info and timing files
        self.directory_path = settings["dir_path"]

        #: ft.ProgressBar: Progress bar for experiment progress
        self.progress_bar = ft.ProgressBar(width=600)

        #: ft.Text: Text for the progress bar that gets updated
        self.progress_bar_text = Text()

        #: ft.Column: Layout to hold progress bar elements
        self.pb_column = Column([self.progress_bar_text, self.progress_bar])

        #: ft.TextField: Dynamic log showing experiment progress text outputs
        self.output_log = TextField(
            # label="Script output log",
            multiline=True,
            max_lines=4,
            min_lines=4,
            read_only=True,
            value="",
            text_size=12,
            border_color=ft.colors.OUTLINE_VARIANT,
            bgcolor=ft.colors.SECONDARY_CONTAINER,
        )

        #: ft.Switch: Toggle to enable or disable showing logs
        self.log_toggle = ft.Switch(
            label="Show output log",
            on_change=self.show_output_log,
            value=False,
        )

        #: Event: Event to control arduino threaded process
        self.stop_threads = Event()

        #: ft.Text: Placeholder container for arduino progress msgs
        self.arduino_step_text = Text()

        #: bool: Whether the Arduino port has been opened
        self.port_opened = False

        #: bool: Whether Arduino has triggered microscope
        self.trig_signal = False

        #: bool: Whether odor delivery sequence has finished
        self.sequence_complete = False

        # Keep track of when the solenoids were activated

        #: list: Contains times that solenoids were activated
        self.time_solenoid_on = []

        #: list: Contains times that solenoids were closed
        self.time_solenoid_off = []

        #: int: Whether a string has been sent to the arduino
        # If sent = 1, then that means a string has been sent to the arduino
        # and we need to wait for it to be done
        self.sent = 0

        #: list: List of times when microscope has been triggered via TTL
        self.time_scope_TTL = []
        self.open_port()
        self.update()

    def open_port(self):
        """Opens arduino port.

        As of Nov 16, 2023, the Arduino board controlling 1% odor valves is
        connected via COM8, and the board controlling 10% odor valves is
        connected via COM7.
        """

        #: serial.Serial: The Serial instance used in this session
        self.arduino = serial.Serial()

        if self.panel_type == "1%":
            #: str: The port to activate, depending on which panel to deliver.
            self.port = "COM8"
        elif self.panel_type == "10%":
            self.port = "COM7"

        # self.arduino.port = "COM8"  # Change COM PORT if COMPort error occurs
        self.arduino.port = self.port
        self.arduino.baudrate = 9600
        self.arduino.timeout = 2
        self.arduino.setRTS(False)

        self.arduino.open()
        self.port_opened = True
        self.progress_bar_text.value = f"Arduino port {self.port} opened."

    def close_port(self):
        """Closes arduino port."""

        self.arduino.close()
        self.port_opened = False

    def get_arduino_msg(self):
        """Gets message back from arduino after sending it a string."""

        if self.arduino.isOpen():
            sent_info = self.arduino.readline().strip()
            arduino_msg = sent_info.decode("utf-8")
        else:
            arduino_msg = None

        return arduino_msg

    def parse_arduino_msg(self, trial: int, solenoid: int):
        """Translates the message sent back from arduino into informative
        timestamps.

        Prints the info into an output log on the main app.

        Args:
            trial: The trial currently being sent to the Arduino board.
            solenoid: The solenoid to activate for the current trial.
        """

        arduino_msg = self.get_arduino_msg()
        print(arduino_msg)

        # Update: check if y is anywhere in the messageReceived in case
        # arduino sends too many at once
        if arduino_msg is None or "y" in arduino_msg:
            pass

        else:
            if arduino_msg == "9":
                self.progress_bar_text.value = (
                    f"Executing Trial {trial+1}/" f"{len(self.solenoid_order)}"
                )
                # Time when microscope has been triggered via TTL
                time_TTL = datetime.datetime.now().isoformat(
                    "|", timespec="milliseconds"
                )
                self.time_scope_TTL.append(time_TTL)

                self.arduino_step_text.value = (
                    f"Trial {trial+1}, Odor "
                    f"{solenoid} microscope triggered at {time_TTL}"
                )

                print(
                    f"Trial {trial+1}, Odor {solenoid} microscope triggered at "
                    f"{time_TTL}"
                )

                self.update_log(trial + 1, solenoid, "9", time_TTL)

            elif arduino_msg == "1":
                time_solenoid_on = datetime.datetime.now().isoformat(
                    "|", timespec="milliseconds"
                )
                self.time_solenoid_on.append(time_solenoid_on)
                self.arduino_step_text.value = (
                    f"Trial {trial+1}, Odor "
                    f"{solenoid} released at {time_solenoid_on}"
                )

                print(
                    f"Trial {trial+1}, Odor {solenoid} released at "
                    f"{time_solenoid_on}"
                )

                self.update_log(trial + 1, solenoid, "1", time_solenoid_on)

            elif arduino_msg == "2":
                time_solenoid_off = datetime.datetime.now().isoformat(
                    "|", timespec="milliseconds"
                )
                self.time_solenoid_off.append(time_solenoid_off)
                self.arduino_step_text.value = (
                    f"Trial {trial+1}, Odor "
                    f"{solenoid} stopped. Delay started at {time_solenoid_off}"
                )

                print(
                    f"Trial {trial+1}, Odor {solenoid} stopped at "
                    f"{time_solenoid_off}"
                )

                self.update_log(trial + 1, solenoid, "2", time_solenoid_off)
                self.save_solenoid_timings(trial)

            elif arduino_msg == "3":
                self.arduino_step_text.value = (
                    f"Trial {trial+1}, Odor "
                    f"{solenoid} delay finished, send next solenoid info"
                )

                print(
                    f"Trial {trial+1}, Odor {solenoid} delay stopped, send next "
                    "solenoid info"
                )

                self.update_log(trial + 1, solenoid, "3", None)

                self.sent = 0

            # self.update()

        self.update()

    def update_log(self, trial: int, odor: int, step: str, isotime: str):
        """Updates the app's output log with Arduino's experiment progress.

        Args:
            trial: The trial currently being sent to the Arduino board.
            odor: The odor being delivered in the current trial.
            step: Integer representing the current step of the delivery process
            isotime: The time of the current step
        """

        if step != "3":
            time_obj = datetime.datetime.fromisoformat(isotime)
            time = time_obj.strftime("%H:%M:%S")
        else:
            time = datetime.datetime.now().strftime("%H:%M:%S")
        step_text_dict = {
            "9": f"microscope triggered",
            "1": f"released",
            "2": f"stopped, delay started",
            "3": f"delay finished, send next solenoid info.",
        }
        new_text = f"{time}: Trial {trial}, Odor {odor} {step_text_dict[step]}"

        if trial == 1 and step == "9":
            self.output_log.value = new_text
        else:
            self.output_log.value = self.output_log.value + "\n" + new_text

        self.update

    def generate_arduino_str(self):
        """Generates arduino execution strings in format "x, y, z".

        x = solenoid number
        y = odor duration (s)
        z = time between odors (s)
        """

        if self.trig_signal == True:
            self.progress_bar_text.value = (
                f"Press Start/Run on Thor Images to start odor delivery"
            )
            for trial in range(len(self.solenoid_order)):
                self.progress_bar.value = trial * (1 / len(self.solenoid_order))
                self.update()
                print(f"doing trial {trial+1}")

                to_be_sent = (
                    f"<{self.solenoid_order[trial]},{self.acq_params['odor_duration']},"
                    f"{self.acq_params['time_btw_odors']}>"
                )

                self.sent = 1

                # Send the information to arduino and wait for something to come back
                self.arduino.write(to_be_sent.encode())
                print(f"to be sent is {to_be_sent}")

                while not self.stop_threads.is_set() and self.sent == 1:
                    # while self.sent == 1:
                    self.parse_arduino_msg(
                        trial,
                        self.solenoid_order[trial],
                    )

                    self.update()

                if self.stop_threads.is_set():
                    break

            if self.stop_threads.is_set():
                self.progress_bar_text.value = (
                    "Experiment aborted. Press "
                    "Reset Settings to start a new experiment, or Start "
                    "Experiment to redo the same odor sequence."
                )

            else:
                self.sequence_complete = True
                self.trig_signal = False
                self.progress_bar.value = len(self.solenoid_order) * (
                    1 / len(self.solenoid_order)
                )

                self.progress_bar_text.value = "Odor delivery sequence complete."

            self.close_port()
            self.update()

            timings_name = (
                f"{self.date}_{self.animal_id}_"
                f"{self.roi}_solenoid_timings_{self.csv_time}.csv"
            )

            self.page.snack_bar.content.value = (
                f"Solenoid timings "
                f"saved to "
                f"{timings_name} in "
                f"experiment "
                f"directory."
            )
            self.page.snack_bar.open = True
            self.page.update()

    def save_solenoid_timings(self, trial: int):
        """Saves the timestamps for when each solenoid was triggered, opened,
        and closed to a .csv file.

        Entries for each trials are added to the csv after each trial has
        been completed, so the file is updated in real-time.

        Args:
            trial: The current trial of the timings being written to the file.
        """
        csv_name = (
            f"{self.date}_{self.animal_id}_{self.roi}_solenoid_timings_"
            f"{self.csv_time}.csv"
        )
        path = os.path.join(self.directory_path, csv_name)

        if trial == 0:
            trial_labels = [trial + 1]
        else:
            trial_labels = list(range(1, trial + 2))

        try:
            timings_df = pd.DataFrame(
                {
                    "Trial": trial_labels,
                    f"Odor {self.panel_type}": self.solenoid_order[: trial + 1],
                    "Microscope Triggered": self.time_scope_TTL,
                    "Solenoid opened": self.time_solenoid_on,
                    "Solenoid closed": self.time_solenoid_off,
                }
            )
        except ValueError:
            pdb.set_trace()

        timings_df.to_csv(path, index=False)

    def show_output_log(self, e):
        """Enable or disable display of experiment output log.

        Args:
            e (event): on_change event from toggling output log switch.
        """

        if self.output_log in self.arduino_layout.content.controls:
            self.arduino_layout.content.controls.remove(self.output_log)
        else:
            self.arduino_layout.content.controls.append(self.output_log)

        self.update()

    def build(self):
        #: ft.Container: Layout containing all the UI elements for Arduino
        # experiment progress.
        self.arduino_layout = Container(
            Column(
                controls=[
                    self.pb_column,
                    self.arduino_step_text,
                    Row(controls=[self.log_toggle]),
                ]
            )
        )

        return self.arduino_layout
