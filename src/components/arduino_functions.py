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
    def __init__(self, page, settings, odor_sequence):
        """
        Defines the class for holding signals sent to the arduino per session
        """
        super().__init__()
        self.page = page
        self.acq_params = settings
        self.solenoid_order = odor_sequence

        self.date = settings["date"]
        self.animal_id = settings["mouse"]
        self.roi = settings["roi"]
        self.directory_path = settings["dir_path"]

        # Progress bar
        self.progress_bar = ft.ProgressBar(width=600)
        # Progress bar text
        self.progress_bar_text = Text()
        self.pb_column = Column([self.progress_bar_text, self.progress_bar])
        self.output_log = TextField(
            # label="Script output log",
            multiline=True,
            max_lines=4,
            min_lines=3,
            read_only=True,
            value="",
            text_size=12,
            border_color=ft.colors.OUTLINE_VARIANT,
            bgcolor=ft.colors.SECONDARY_CONTAINER,
        )

        self.log_toggle = ft.Switch(
            label="Show output log",
            on_change=self.show_output_log,
            value=False,
        )

        self.stop_threads = Event()

        # Plateholder container for arduino progress msgs
        # self.arduino_step_text = Text("Initial arduino step progress")
        self.arduino_step_text = Text()

        self.port_opened = False
        self.trig_signal = False  # Whether Arduino has triggered microscope
        self.sequence_complete = (
            False  # Whether odor delivery sequence has finished
        )

        # Keep track of when the solenoids were activated
        self.time_solenoid_on = (
            []
        )  # Contains times that solenoids were activated
        self.time_solenoid_off = (
            []
        )  # Contains times that solenoids were closed

        # if sent = 1, then that means a string has been sent to the arduino
        # and we need to wait for it to be done
        self.sent = 0

        self.time_scope_TTL = []

        # self.generate_arduino_str()
        self.open_port()
        self.update()

    def open_port(self):
        """
        Opens arduino port
        """
        self.arduino = serial.Serial()

        self.arduino.port = "COM7"  # Change COM PORT if COMPort error occurs
        self.arduino.baudrate = 9600
        self.arduino.timeout = 2
        self.arduino.setRTS(False)

        self.arduino.open()
        self.port_opened = True
        self.progress_bar_text.value = "Arduino port opened."

    def close_port(self):
        """
        Closes arduino port
        """
        self.arduino.close()
        self.port_opened = False

    def get_arduino_msg(self):
        """
        Gets message back from arduino after sending it str
        """
        if self.arduino.isOpen():
            sent_info = self.arduino.readline().strip()
            arduino_msg = sent_info.decode("utf-8")
        else:
            arduino_msg = None

        return arduino_msg

    def parse_arduino_msg_test(self, trial, solenoid):
        """
        Test version without actual arduino input
        """
        time_TTL = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )
        self.time_scope_TTL.append(time_TTL)

        self.arduino_step_text.value = (
            f"trial {trial+1}, odor "
            f"{solenoid} microscope triggered at {time_TTL}"
        )

        print(
            f"trial {trial+1}, odor {solenoid} microscope triggered at "
            f"{time_TTL}"
        )

        self.output_log.value = (
            self.output_log.value + "\n" + self.arduino_step_text.value
        )
        print(f"output log value is {self.output_log.value}")

        self.update()
        time.sleep(1)

        time_solenoid_on = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )
        self.time_solenoid_on.append(time_solenoid_on)
        self.arduino_step_text.value = (
            f"trial {trial+1}, odor "
            f"{solenoid} released at {time_solenoid_on}"
        )

        print(
            f"trial {trial+1}, odor {solenoid} released at "
            f"{time_solenoid_on}"
        )

        self.output_log.value = (
            self.output_log.value + "\n" + self.arduino_step_text.value
        )
        print(f"output log value is {self.output_log.value}")

        self.update()
        time.sleep(1)

        time_solenoid_off = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )
        self.time_solenoid_off.append(time_solenoid_off)
        self.arduino_step_text.value = (
            f"trial {trial+1}, odor "
            f"{solenoid} stopped at {time_solenoid_off}"
        )

        print(
            f"trial {trial+1}, odor {solenoid} stopped at "
            f"{time_solenoid_off}"
        )

        self.output_log.value = (
            self.output_log.value + "\n" + self.arduino_step_text.value
        )
        print(f"output log value is {self.output_log.value}")

        self.update()
        time.sleep(1)

        self.arduino_step_text.value = (
            f"trial {trial+1}, odor "
            f"{solenoid} delay stopped, send next solenoid info"
        )

        print(
            f"trial {trial+1}, odor {solenoid} delay stopped, send next "
            "solenoid info"
        )

        self.output_log.value = (
            self.arduino_step_text.value + "\n" + self.output_log.value
        )
        print(f"output log value is {self.output_log.value}")

        self.sent = 0
        self.update()

    def parse_arduino_msg(self, trial, solenoid):
        """
        Translates the message sent back from arduino into informative
        timestamps. Prints the info into placeholder textbox
        """
        arduino_msg = self.get_arduino_msg()
        print(arduino_msg)
        # self.arduino_step_text.value = ""

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
                self.save_solenoid_timings_test(trial)

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

    def update_log(self, trial, odor, step, isotime):
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
        """
        Generates arduino execution strs in format "x, y, z" where
        x = solenoid number
        y = odor duration (s)
        z = time between odors (s)
        """

        print("generate_arduino_str called")
        if self.trig_signal == True:
            self.progress_bar_text.value = (
                f"Press Start on Thor Images to start odor delivery"
            )
            for trial in range(len(self.solenoid_order)):
                self.progress_bar.value = trial * (
                    1 / len(self.solenoid_order)
                )
                self.update()
                print(f"doing trial {trial+1}")

                to_be_sent = (
                    # f"{solenoid},{self.acq_params.odor_duration},"
                    f"<{self.solenoid_order[trial]},{self.acq_params['odor_duration']},"
                    f"{self.acq_params['time_btw_odors']}>"
                )

                self.sent = 1

                # Send the information to arduino and wait for something to come back
                # st.session_state.arduino.write(to_be_sent.encode())
                self.arduino.write(to_be_sent.encode())
                print(f"to be sent is {to_be_sent}")

                while self.sent == 1:
                    self.parse_arduino_msg(
                        trial,
                        self.solenoid_order[trial],
                    )

                    self.update()

            self.sequence_complete = True
            self.trig_signal = False
            self.progress_bar.value = len(self.solenoid_order) * (
                1 / len(self.solenoid_order)
            )

            self.progress_bar_text.value = "Odor delivery sequence complete."
            self.close_port()
            self.update()

    def thread_generate_arduino_str(self):
        """
        Generates arduino execution strs in format "x, y, z" where
        x = solenoid number
        y = odor duration (s)
        z = time between odors (s)
        """

        print("generate_arduino_str called")
        if self.trig_signal == True:
            self.progress_bar_text.value = (
                f"Press Start on Thor Images to start odor delivery"
            )
            for trial in range(len(self.solenoid_order)):
                self.progress_bar.value = trial * (
                    1 / len(self.solenoid_order)
                )
                self.update()
                print(f"doing trial {trial+1}")

                to_be_sent = (
                    # f"{solenoid},{self.acq_params.odor_duration},"
                    f"<{self.solenoid_order[trial]},{self.acq_params['odor_duration']},"
                    f"{self.acq_params['time_btw_odors']}>"
                )

                self.sent = 1

                # Send the information to arduino and wait for something to come back
                # st.session_state.arduino.write(to_be_sent.encode())
                self.arduino.write(to_be_sent.encode())
                print(f"to be sent is {to_be_sent}")

                while not self.stop_threads.is_set() and self.sent == 1:
                    # while self.sent == 1:
                    self.parse_arduino_msg(
                        trial,
                        self.solenoid_order[trial],
                    )

                    # self.save_solenoid_timings_test(trial)

                    self.update()

                if self.stop_threads.is_set():
                    break

            if self.stop_threads.is_set():
                self.progress_bar_text.value = (
                    "Experiment aborted. Press "
                    "Reset Settings to start a new experiment, or Start "
                    "Experiment to redo the same odor sequence."
                )
                # self.close_port()
                # self.update()
                # break
            else:
                self.sequence_complete = True
                self.trig_signal = False
                self.progress_bar.value = len(self.solenoid_order) * (
                    1 / len(self.solenoid_order)
                )

                self.progress_bar_text.value = (
                    "Odor delivery sequence complete."
                )
                # self.close_port()
                # self.update()

            self.close_port()
            self.update()

            timings_name = (
                f"{self.date}_{self.animal_id}_"
                f"{self.roi}_solenoid_timings.csv"
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

    def generate_arduino_str_test(self):
        """
        Generates arduino execution strs in format "x, y, z" where
        x = solenoid number
        y = odor duration (s)
        z = time between odors (s)
        """
        self.trig_signal = True  # for testing only
        if self.trig_signal == True:
            for trial in range(len(self.solenoid_order)):
                if trial == 0:
                    self.progress_bar_text.value = (
                        f"Press Start on Thor Images to start Trial {trial+1}/"
                        f"{len(self.solenoid_order)}"
                    )
                else:
                    self.progress_bar_text.value = (
                        f"Executing Trial {trial+1}/"
                        f"{len(self.solenoid_order)}"
                    )
                self.progress_bar.value = trial * (
                    1 / len(self.solenoid_order)
                )
                self.update()
                print(f"doing trial {trial+1}")

                to_be_sent = (
                    # f"{solenoid},{self.acq_params.odor_duration},"
                    f"{self.solenoid_order[trial]},{self.acq_params['odor_duration']},"
                    f"{self.acq_params['time_btw_odors']}"
                )

                self.sent = 1

                # Send the information to arduino and wait for something to come back
                # st.session_state.arduino.write(to_be_sent.encode())
                # self.arduino.write(to_be_sent.encode())

                while self.sent == 1:
                    self.parse_arduino_msg_test(
                        trial,
                        self.solenoid_order[trial],
                    )

                    # # Mark end after last trial
                    # if trial + 1 == len(bar):
                    self.update()

            self.sequence_complete = True
            self.trig_signal = False
            self.progress_bar.value = len(self.solenoid_order) * (
                1 / len(self.solenoid_order)
            )

            self.progress_bar_text.value = "Odor delivery sequence complete."
            # self.close_port()
            self.update()

    def save_solenoid_timings(self):
        """
        Saves the timestamps for when each solenoid was triggered, opened,
        and closed to a .csv file.
        """
        if self.stop_threads.is_set():
            pass
        else:
            csv_name = (
                f"{self.date}_{self.animal_id}_{self.roi}_solenoid_timings.csv"
            )
            path = os.path.join(self.directory_path, csv_name)

            trial_labels = list(range(1, len(self.solenoid_order) + 1))
            timings_df = pd.DataFrame(
                {
                    "Trial": trial_labels,
                    "Odor #": self.solenoid_order,
                    "Microscope Triggered": self.time_scope_TTL,
                    "Solenoid opened": self.time_solenoid_on,
                    "Solenoid closed": self.time_solenoid_off,
                }
            )

            timings_df.to_csv(path, index=False)

            timings_name = (
                f"{self.date}_{self.animal_id}_"
                f"{self.roi}_solenoid_timings.csv"
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

    def save_solenoid_timings_test(self, trial):
        """
        Saves the timestamps for when each solenoid was triggered, opened,
        and closed to a .csv file.
        """
        csv_name = (
            f"{self.date}_{self.animal_id}_{self.roi}_solenoid_timings.csv"
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
                    "Odor #": self.solenoid_order[: trial + 1],
                    "Microscope Triggered": self.time_scope_TTL,
                    "Solenoid opened": self.time_solenoid_on,
                    "Solenoid closed": self.time_solenoid_off,
                }
            )
        except ValueError:
            pdb.set_trace()

        timings_df.to_csv(path, index=False)

        timings_name = (
            f"{self.date}_{self.animal_id}_" f"{self.roi}_solenoid_timings.csv"
        )

        # self.page.snack_bar.content.value = (
        #     f"Solenoid timings "
        #     f"saved to "
        #     f"{timings_name} in "
        #     f"experiment "
        #     f"directory."
        # )
        # self.page.snack_bar.open = True
        # self.page.update()

    def show_output_log(self, e):
        """"""
        if self.output_log in self.arduino_layout.content.controls:
            self.arduino_layout.content.controls.remove(self.output_log)
        else:
            self.arduino_layout.content.controls.append(self.output_log)

        self.update()

    def build(self):
        self.arduino_layout = Container(
            Column(
                controls=[
                    self.pb_column,
                    self.arduino_step_text,
                    # self.log_toggle
                    Row(controls=[self.log_toggle]),
                ]
            )
        )

        return self.arduino_layout
