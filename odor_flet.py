import flet as ft
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Container,
    Text,
    icons,
)

import pandas as pd
import datetime
import random
import serial
import os
import pdb


# def initialize_arduino():
#     """
#     Initiate the Arduino
#     """
#     arduino = serial.Serial()

#     arduino.port = "COM7"  # Change COM PORT if COMPort error occurs
#     arduino.baudrate = 9600
#     arduino.timeout = 2
#     arduino.setRTS(FALSE)
#     # time.sleep(2)
#     # two seconds for arduino to reset and port to open
#     arduino.open()

#     return arduino


def close_arduino(arduino):
    """
    Closes the arduino connection
    """
    arduino.close()


def get_arduino_msg(arduino):
    """
    Gets message back from arduino after sending it str
    """

    sent_info = arduino.readline().strip()
    decode_info = sent_info.decode("utf-8")

    return decode_info


def randomize_trials(num_odors, num_trials, button=False):
    """
    Randomizes the order of odor delivery
    """
    trials = list(range(1, int(num_odors) + 1)) * int(num_trials)
    random.shuffle(trials)

    if button:
        pass

    return trials


def make_trials_df(trials):
    """
    Puts odor trials into a df
    """
    trial_labels = list(range(1, len(trials) + 1))
    trials_df = pd.DataFrame({"Trial": trial_labels, "Odor #": trials})

    return trials_df


class ArduinoSession:
    """
    Defines the class for holding signals sent to the arduino per session
    """

    def __init__(self, session_params, odor_sequence):
        self.acq_params = session_params

        self.trig_signal = False  # Whether Arduino has triggered microscope
        self.delay_time = 0  # Time btw odors? don't think I need

        self.sequence_complete = (
            False  # Whether odor delivery sequence has finished
        )

        self.solenoid_order = odor_sequence  # Double check

        ###For predicted timings:
        self.trigger = 100  # in milliseconds   what is this??
        self.iniStart = datetime.datetime.now()
        self.iniHour = (self.iniStart).hour
        self.iniMinute = (self.iniStart).minute
        self.iniSec = (self.iniStart).second
        self.iniMicroSec = (self.iniStart).microsecond
        self.iniMilliSec = (
            self.iniMicroSec
        ) / 1000  # only has microseconds, which is 1/1000 milliseconds

        # Testing new format to directly go into miliseconds
        self.init_time = datetime.datetime.now().isoformat(
            "|", timespec="milliseconds"
        )

        ###Keep track of when the solenoids were activated
        self.time_solenoid_on = (
            []
        )  # Contains times that solenoids were activated
        self.time_solenoid_off = (
            []
        )  # Contains times that solenoids were closed
        self.sent = 0  # if sent = 1, then that means a string has been sent to the arduino and we need to wait for it to be done
        self.timeTTLName = "TTL to microscope sent at: "
        self.time_scope_TTL = []


class DeliveryApp:
    def __init__(self, page: Page):
        self.page = page
        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result
        )
        self.directory_path = Text(col={"sm": 8})
        page.overlay.append(self.get_directory_dialog)

        self.initial_setup()
        self.create_settings_fields()
        self.create_buttons()
        row1, row2, row3, row4 = self.arrange_settings_fields()
        self.arrange_view(row1, row2, row3, row4)

        self.page.update()

    def initial_setup(self):
        self.page.title = "Odor Delivery App"

    # Checks whether all settings have been entered and create save button
    def check_settings_complete(self, e):
        if (
            ""
            in [
                self.directory_path.value,
                self.animal_id.value,
                self.roi.value,
                self.num_odors.value,
                self.num_trials.value,
                self.odor_duration.value,
                self.time_btw_odors.value,
                self.randomize_option.value,
            ]
            or self.num_odors.value is None
            or self.directory_path.value is None
        ):
            self.save_settings_btn.disabled = True

        else:
            self.save_settings_btn.disabled = False

        self.page.update()

    # Saves input values to dict, to pass into ArduinoSession
    def save_settings_clicked(self, e):
        now_date = datetime.datetime.now()
        settings_dict = {
            "dir_path": self.directory_path.value,
            "mouse": self.animal_id.value,
            "roi": self.roi.value,
            "date": now_date.strftime("%y%m%d"),
            "num_odors": self.num_odors.value,
            "num_trials": self.num_trials.value,
            "odor_duration": self.odor_duration.value,
            "time_btw_odors": self.time_btw_odors.value,
            "randomize_trials": self.randomize_option.value,
        }

        if self.randomize_option.value is True:
            randomized_trials = randomize_trials(
                self.num_odors.value, self.num_trials.value
            )

            self.print_trial_order(randomized_trials)

        self.page.update()

        print(settings_dict["date"])

    # Open directory dialog
    def get_directory_result(self, e: FilePickerResultEvent):
        self.directory_path.value = e.path if e.path else "Cancelled!"
        self.directory_path.update()
        self.check_settings_complete(e)

    def create_buttons(self):
        self.pick_directory_btn = ElevatedButton(
            "Open directory",
            icon=icons.FOLDER_OPEN,
            col={"sm": 4},
            on_click=lambda _: self.get_directory_dialog.get_directory_path(),
            disabled=self.page.web,
        )

        self.randomize_option = ft.Switch(
            label="Shuffle trials", value=True, col={"sm": 4}
        )

        self.save_settings_btn = ElevatedButton(
            "Save Settings",
            icon=icons.SAVE_ALT_ROUNDED,
            on_click=self.save_settings_clicked,
            col={"sm": 4},
            disabled=True,
        )

    # Arranges setting fields in rows
    def arrange_settings_fields(self):
        settings_r1 = ft.ResponsiveRow(
            [
                self.pick_directory_btn,
                self.directory_path,
            ]
        )
        settings_r2 = ft.ResponsiveRow(
            [
                self.animal_id,
                self.roi,
                self.num_odors,
            ],
        )

        settings_r3 = ft.ResponsiveRow(
            [
                self.odor_duration,
                self.time_btw_odors,
                self.num_trials,
            ]
        )

        # settings_r4 = ft.ResponsiveRow(
        #     [self.randomize_option, self.save_settings_btn]
        # )

        settings_r4 = ft.ResponsiveRow(
            [
                self.randomize_option,
                SaveSettingsButton(
                    self.directory_path,
                    self.animal_id.value,
                    self.roi.value,
                    self.num_odors.value,
                    self.num_trials.value,
                    self.odor_duration.value,
                    self.time_btw_odors.value,
                    self.randomize_option.value,
                ),
            ]
        )

        return settings_r1, settings_r2, settings_r3, settings_r4

    def print_trial_order(self, trials):
        """
        Prints a table listing the trial number and odor used for each trial
        """
        trials_df = make_trials_df(trials).T
        trial_heading = ft.Markdown("**Odor order by trial:**")

        # trials_table = ft.DataTable()
        for trials_num in range(len(trials_df.columns)):
            self.raw_trials_table.columns.append(
                ft.DataColumn(ft.Text(trials_df.columns[trials_num]))
            )
        self.raw_trials_table.rows.append(
            ft.DataRow(cells=trials_df.loc["Odor #"].tolist())
        )
        self.trials_table[0] = self.raw_trials_table

        # self.view2 = ft.Column(
        #     width=600,
        #     controls=[trials_table],
        # )

        # self.page.add(self.view2)
        # self.page.update()

    def arrange_view(self, row1, row2, row3, row4):
        page_title = Text(
            "Delivery Settings", style=ft.TextThemeStyle.DISPLAY_MEDIUM
        )
        directory_prompt = Text(
            "Select experiment folder to save solenoid info"
        )

        # Empty space for trial order
        self.raw_trials_table = ft.DataTable()
        self.trials_table = [self.raw_trials_table]
        self.trials_table_row = ft.Container(ft.Row(self.trials_table))

        self.view = ft.Column(
            width=600,
            controls=[
                page_title,
                directory_prompt,
                row1,
                row2,
                row3,
                row4,
                self.trials_table_row,
            ],
        )

        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.window_width = 700
        self.page.window_height = 600
        # page.window_resizable = False

        self.page.add(self.view)


# Experiment settings input fields
class ExperimentSettings(ft.UserControl):
    def build(self):
        return ft.Column()

    # Creates setting input fields
    def create_settings_fields(self):
        self.animal_id = ft.TextField(
            value="",
            label="Animal ID",
            hint_text="e.g. 123456-1-2",
            col={"sm": 4},
            on_change=self.check_settings_complete,
        )
        self.roi = ft.TextField(
            value="",
            label="ROI #",
            col={"sm": 4},
            on_change=self.check_settings_complete,
        )

        self.num_odors = ft.Dropdown(
            value="",
            label="# of odors",
            width=100,
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=self.check_settings_complete,
        )

        self.num_trials = ft.TextField(
            value="",
            label="# Trials/odor",
            col={"sm": 4},
            on_change=self.check_settings_complete,
        )
        self.odor_duration = ft.TextField(
            value=1,
            label="Odor duration (s)",
            col={"sm": 4},
            on_change=self.check_settings_complete,
        )
        self.time_btw_odors = ft.TextField(
            value=10,
            label="Time between odors (s)",
            col={"sm": 4},
            on_change=self.check_settings_complete,
        )

    # Arranges setting fields in rows
    def arrange_settings_fields(self):
        settings_r1 = ft.ResponsiveRow(
            [
                self.pick_directory_btn,
                self.directory_path,
            ]
        )
        settings_r2 = ft.ResponsiveRow(
            [
                self.animal_id,
                self.roi,
                self.num_odors,
            ],
        )

        settings_r3 = ft.ResponsiveRow(
            [
                self.odor_duration,
                self.time_btw_odors,
                self.num_trials,
            ]
        )

        # settings_r4 = ft.ResponsiveRow(
        #     [self.randomize_option, self.save_settings_btn]
        # )

        settings_r4 = ft.ResponsiveRow(
            [
                self.randomize_option,
                SaveSettingsButton(
                    self.directory_path,
                    self.animal_id.value,
                    self.roi.value,
                    self.num_odors.value,
                    self.num_trials.value,
                    self.odor_duration.value,
                    self.time_btw_odors.value,
                    self.randomize_option.value,
                ),
            ]
        )

        return settings_r1, settings_r2, settings_r3, settings_r4

    def check_settings_complete(self, e):
        if (
            ""
            in [
                self.directory_path.value,
                self.animal_id.value,
                self.roi.value,
                self.num_odors.value,
                self.num_trials.value,
                self.odor_duration.value,
                self.time_btw_odors.value,
                self.randomize_option.value,
            ]
            or self.num_odors.value is None
            or self.directory_path.value is None
        ):
            self.save_settings_btn.disabled = True

        else:
            self.save_settings_btn.disabled = False

        self.page.update()


# Save settings button
class SaveSettingsButton(ft.UserControl):
    def __init__(
        self,
        directory_path,
        animal_id,
        roi,
        num_odors,
        num_trials,
        odor_duration,
        time_btw_odors,
        randomize_option,
    ):
        super().__init__()

        self.directory_path = directory_path
        self.animal_id = animal_id
        self.roi = roi
        self.num_odors = num_odors
        self.num_trials = num_trials
        self.odor_duration = odor_duration
        self.time_btw_odors = time_btw_odors
        self.randomize_option = randomize_option

    def print_trial_order(self, trials):
        """
        Prints a table listing the trial number and odor used for each trial
        """
        trials_df = make_trials_df(trials).T
        trial_heading = ft.Markdown("**Odor order by trial:**")

        # trials_table = ft.DataTable()
        for trials_num in range(len(trials_df.columns)):
            self.raw_trials_table.columns.append(
                ft.DataColumn(ft.Text(trials_df.columns[trials_num]))
            )
        self.raw_trials_table.rows.append(
            ft.DataRow(cells=trials_df.loc["Odor #"].tolist())
        )
        self.trials_table[0] = self.raw_trials_table

    def clicked(self, e):
        now_date = datetime.datetime.now()
        settings_dict = {
            "dir_path": self.directory_path,
            "mouse": self.animal_id,
            "roi": self.roi,
            "date": now_date.strftime("%y%m%d"),
            "num_odors": self.num_odors,
            "num_trials": self.num_trials,
            "odor_duration": self.odor_duration,
            "time_btw_odors": self.time_btw_odors,
            "randomize_trials": self.randomize_option,
        }

        if self.randomize_option is True:
            randomized_trials = randomize_trials(
                self.num_odors, self.num_trials
            )

            self.print_trial_order(randomized_trials)

    def build(self):
        self.raw_trials_table = ft.DataTable()

        button = ElevatedButton(
            "Save Settings",
            icon=icons.SAVE_ALT_ROUNDED,
            on_click=self.clicked,
            col={"sm": 4},
            disabled=False,
        )
        # self.update()

        return ft.Row([button, self.raw_trials_table])


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"
        app = DeliveryApp(page)
        # page.add(app) # idk why this doesn't work
        page.update()

    # ft.app(target=main, view=ft.WEB_BROWSER)
    ft.app(target=main)
