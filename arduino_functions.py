import flet as ft
from flet import (
    UserControl,
    Column,
    Container,
    Text,
)

import datetime
import serial
import pdb
import time


class ArduinoSession(UserControl):
    def __init__(self, page, settings, odor_sequence, pb, pb_text):
        """
        Defines the class for holding signals sent to the arduino per session
        """
        super().__init__()
        self.page = page
        self.acq_params = settings
        self.solenoid_order = odor_sequence
        self.progress_bar = pb
        self.progress_bar_text = pb_text

        # Plateholder container for arduino progress msgs
        # self.arduino_step_text = Text("Initial arduino step progress")
        self.arduino_step_text = Text()

        # # Progress bar
        # self.progress_bar = ft.ProgressBar(width=600)
        # # Progress bar text
        # self.progress_bar_text = Text()
        # self.pb_column = Column([self.progress_bar_text, self.progress_bar])

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
            arduino_msg = self.sent_info.decode("utf-8")
        else:
            arduino_msg = None

        return arduino_msg

    def parse_arduino_msg(self, trial, solenoid):
        """
        Translates the message sent back from arduino into informative
        timestamps. Prints the info into placeholder textbox
        """
        # arduino_msg_received = self.get_arduino_msg()
        # arduino_msg = self.get_arduino_msg()

        # Testing without Arduino

        time_TTL = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )
        self.time_scope_TTL.append(time_TTL)

        self.arduino_step_text.value = f"trial {trial+1}, odor "
        f"{solenoid} microscope triggered at {time_TTL}"

        print(
            f"trial {trial+1}, odor {solenoid} microscope triggered at "
            f"{time_TTL}"
        )

        time.sleep(1)

        time_solenoid_on = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )
        self.time_solenoid_on.append(time_solenoid_on)
        self.arduino_step_text.value = f"trial {trial+1}, odor "
        f"{solenoid} released at {time_solenoid_on}"

        print(
            f"trial {trial+1}, odor {solenoid} released at "
            f"{time_solenoid_on}"
        )

        time.sleep(1)

        time_solenoid_off = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )
        self.time_solenoid_off.append(time_solenoid_off)
        self.arduino_step_text.value = f"trial {trial+1}, odor "
        f"{solenoid} stopped at {time_solenoid_off}"

        print(
            f"trial {trial+1}, odor {solenoid} stopped at "
            f"{time_solenoid_off}"
        )

        time.sleep(1)

        self.arduino_step_text.value = f"trial {trial+1}, odor "
        f"{solenoid} delay stopped, send next solenoid info"

        print(
            f"trial {trial+1}, odor {solenoid} delay stopped, send next "
            "solenoid info"
        )

        self.sent = 0
        self.update()

        # # Update: check if y is anywhere in the messageReceived in case arduino sends too many at once
        # if arduino_msg is None or "y" in arduino_msg:
        #     pass

        # else:
        #     if arduino_msg == "9":
        #         # Time when microscope has been triggered via TTL
        #         time_TTL = datetime.datetime.now().isoformat(
        #             "|", timespec="milliseconds"
        #         )
        #         self.time_scope_TTL.append(time_TTL)

        #         self.arduino_step_text.value = f"trial {trial+1}, odor "
        #         f"{solenoid} microscope triggered at {time_TTL}"

        #         print(
        #             f"trial {trial+1}, odor {solenoid} microscope triggered at "
        #             f"{time_TTL}"
        #         )

        #     elif arduino_msg == "1":
        #         time_solenoid_on = datetime.datetime.now().isoformat(
        #             "|", timespec="milliseconds"
        #         )
        #         self.time_solenoid_on.append(time_solenoid_on)
        #         self.arduino_step_text.value = f"trial {trial+1}, odor "
        #         f"{solenoid} released at {time_solenoid_on}"

        #         print(
        #             f"trial {trial+1}, odor {solenoid} released at "
        #             f"{time_solenoid_on}"
        #         )

        #     elif arduino_msg == "2":
        #         time_solenoid_off = datetime.datetime.now().isoformat(
        #             "|", timespec="milliseconds"
        #         )
        #         self.time_solenoid_off.append(time_solenoid_off)
        #         self.arduino_step_text.value = f"trial {trial+1}, odor "
        #         f"{solenoid} stopped at {time_solenoid_off}"

        #         print(
        #             f"trial {trial+1}, odor {solenoid} stopped at "
        #             f"{time_solenoid_off}"
        #         )

        #     elif arduino_msg == "3":
        #         self.arduino_step_text.value = f"trial {trial+1}, odor "
        #         f"{solenoid} delay stopped, send next solenoid info"

        #         print(
        #             f"trial {trial+1}, odor {solenoid} delay stopped, send next "
        #             "solenoid info"
        #         )

        #         # if trial + 1 != self.num_trials:
        #         #     placeholder.info(
        #         #         f"trial {trial+1}, odor {solenoid} delay stopped, send next "
        #         #         "solenoid info"
        #         #     )

        #         #     print(
        #         #         f"trial {trial+1}, odor {solenoid} delay stopped, send next "
        #         #         "solenoid info"
        #         #     )
        #         # else:
        #         #     placeholder.info("Odor delivery sequence complete.")
        #         #     self.sequence_complete = True

        #         self.sent = 0

        # self.update()

    def generate_arduino_str(self):
        """
        Generates arduino execution strs in format "x, y, z" where
        x = solenoid number
        y = odor duration (s)
        z = time between odors (s)
        """
        self.trig_signal = True  # for testing only
        if self.trig_signal == True:
            # Adds progress bar
            # bar = stqdm(
            #     range(len(self.solenoid_order)), desc=f"Executing Trial"
            # )

            # for solenoid in self.solenoid_order:
            for trial in range(len(self.solenoid_order)):
                self.progress_bar_text.value = f"Executing Trial {trial+1}"
                self.progress_bar.value = trial * (
                    1 / len(self.solenoid_order)
                )
                # self.update()
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
                    self.parse_arduino_msg(
                        trial,
                        self.solenoid_order[trial],
                    )

                    # # Mark end after last trial
                    # if trial + 1 == len(bar):
                    self.update()

            self.sequence_complete = True
            self.trig_signal = False

            self.progress_bar_text.value = "Odor delivery sequence complete."

            self.update()

        # st.info("Experiment finished.")
        # else:
        # st.info("Already finished.")

    def build(self):
        self.arduino_layout = Container(
            Column(
                controls=[
                    # self.progress_bar_text,
                    # self.progress_bar,
                    # self.arduino_step_text
                    Text("arduino_layout here"),
                ]
            )
        )

        return self.arduino_layout