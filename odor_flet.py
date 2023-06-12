import flet as ft
from flet import (
    UserControl,
    TextField,
    Ref,
    Column,
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Container,
    Text,
    icons,
)

from simpledt import DataFrame
import pandas as pd
import datetime
import random
import serial
import os
import pdb


class ArduinoSession:
    """
    Defines the class for holding signals sent to the arduino per session
    """

    def __init__(self, settings, odor_sequence):
        self.settings = settings
        self.solenoid_order = odor_sequence
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
            self.sent_info


class SettingsFields(UserControl):
    def __init__(
        self,
        # ref: Ref = None,
        label: str = "",
        on_change=None,
    ):
        super().__init__()
        self.label = label

        self.textfield_dict = {
            "Animal ID": {"value": ""},
            "ROI": {"value": ""},
            "# Trials/odor": {"value": ""},
            "Odor duration (s)": {"value": "1"},
            "Time between odors (s)": {"value": "10"},
        }

        self.text_field = TextField(
            value=self.textfield_dict[self.label]["value"],
            label=label,
            on_change=on_change,
        )

        if self.label == "Animal ID":
            self.text_field.hint_text = "e.g. 123456-1-2"

    def reset(self):
        self.text_field.value = self.textfield_dict[self.label]["value"]
        self.update()

    def build(self):
        return self.text_field


class TestSettingsLayout(UserControl):
    def __init__(
        self,
        page: Page,
        directory_path,
        check_complete,
    ):
        super().__init__()

        self.page = page
        self.directory_path = directory_path
        self.settings_dict = None
        self.saved_click = False

        self.animal_id = SettingsFields(
            # ref=self.textfield1_ref,
            label="Animal ID",
            on_change=check_complete,
        )

        self.roi = SettingsFields(label="ROI", on_change=check_complete)

        self.num_odors = ft.Dropdown(
            value="",
            label="# of odors",
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            # alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=check_complete,
        )
        self.num_trials = SettingsFields(
            label="# Trials/odor", on_change=check_complete
        )
        self.odor_duration = SettingsFields(
            label="Odor duration (s)", on_change=check_complete
        )
        self.time_btw_odors = SettingsFields(
            label="Time between odors (s)", on_change=check_complete
        )

        # self.create_settings_fields()
        self.arrange_settings_fields()

    def create_settings_fields(self):
        # self.textfield1_ref = Ref[SettingsFields]()
        self.animal_id = SettingsFields(
            # ref=self.textfield1_ref,
            label="Animal ID",
            on_change=self.check_settings_complete,
        )

        self.roi = SettingsFields(
            label="ROI", on_change=self.check_settings_complete
        )

        self.num_odors = ft.Dropdown(
            value="",
            label="# of odors",
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            # alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=self.check_settings_complete,
        )
        self.num_trials = SettingsFields(
            label="# Trials/odor", on_change=self.check_settings_complete
        )
        self.odor_duration = SettingsFields(
            label="Odor duration (s)", on_change=self.check_settings_complete
        )
        self.time_btw_odors = SettingsFields(
            label="Time between odors (s)",
            on_change=self.check_settings_complete,
        )

    # Arranges setting fields in rows
    def arrange_settings_fields(self):
        self.row1 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.animal_id]),
                Column(col={"sm": 4}, controls=[self.roi]),
                Column(col={"sm": 4}, controls=[self.num_odors]),
            ]
        )

        self.row2 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.odor_duration]),
                Column(col={"sm": 4}, controls=[self.time_btw_odors]),
                Column(col={"sm": 4}, controls=[self.num_trials]),
            ]
        )

    def reset_settings_clicked(self, e):
        self.settings_dict = None
        self.animal_id.reset()
        self.roi.reset()
        self.num_odors.value = ""
        self.num_trials.reset()
        self.odor_duration.reset()
        self.time_btw_odors.reset()

        self.disable_settings_fields(disable=False)

        self.update()

    def disable_settings_fields(self, disable):
        self.animal_id.disabled = disable
        self.roi.disabled = disable
        self.num_odors.disabled = disable
        self.num_trials.disabled = disable
        self.odor_duration.disabled = disable
        self.time_btw_odors.disabled = disable

        self.update()

    def build(self):
        return ft.Column(
            controls=[
                self.row1,
                self.row2,
            ],
        )


class TrialOrderTable(UserControl):
    def __init__(self, page, randomize, num_trials, num_odors, reset):
        super().__init__()
        self.page = page

        self.randomize = randomize
        self.exp_display_content = Container()

        if reset is False:
            self.num_trials = num_trials
            self.num_odors = num_odors

            if self.num_trials != "" and self.num_odors != "":
                if self.randomize is True:
                    self.randomize_trials(repeat=False)
                else:
                    self.make_nonrandom_trials()
                self.make_trials_df()
                self.display_trial_order()

    def make_nonrandom_trials(self):
        self.trials = self.trials = (
            list(range(1, self.num_odors + 1)) * self.num_trials
        )
        self.update()

    def randomize_trials(self, repeat, e=None):
        if repeat is False:
            self.trials = list(range(1, self.num_odors + 1)) * self.num_trials
        random.shuffle(self.trials)

        if repeat is True:
            self.make_trials_df()
            self.display_trial_order()
            print("randomize_trials repeat called")
        self.update()

    def make_trials_df(self):
        """
        Puts odor trials into a df
        """
        self.trials_df = pd.DataFrame(self.trials)
        self.trials_df.rename(index=lambda s: s + 1, inplace=True)

    def display_trial_order(self):
        # Using simpledt package fixes the page.add(DataTable) issue
        # https://github.com/StanMathers/simple-datatable

        simplet_df = DataFrame(self.trials_df.T)
        self.simple_dt = simplet_df.datatable

        # Add Trial/Odor labels to table
        self.simple_dt.columns.insert(0, ft.DataColumn(ft.Text("Trial")))
        self.simple_dt.rows[0].cells.insert(
            0, ft.DataCell(content=Text("Odor"))
        )

        self.simple_dt.column_spacing = 20
        self.simple_dt.heading_row_height = 25
        self.simple_dt.data_row_height = 40
        self.simple_dt.horizontal_lines = ft.border.BorderSide(
            2, ft.colors.ON_SECONDARY
        )
        self.simple_dt.vertical_lines = ft.border.BorderSide(
            1, ft.colors.ON_SECONDARY
        )

        self.simple_dt.heading_row_color = ft.colors.SECONDARY_CONTAINER
        # self.simple_dt.heading_text_style = ft.TextStyle(
        #     color=ft.colors.OUTLINE_VARIANT
        # )

        self.exp_display_content.content = Row(
            controls=[self.simple_dt], scroll="auto"
        )

        self.update()

    def build(self):
        self.info_layout = Container(content=self.exp_display_content)
        print("TrialOrderTable build() called")

        return self.info_layout


class ExperimentProgressLayout(UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page

        self.started_text = Text("Experiment in progress...")

    def build(self):
        self.layout = Column(
            controls=[
                self.started_text,
            ]
        )

        return self.layout


class OdorDeliveryApp(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Snack bar init"), bgcolor=ft.colors.SECONDARY
        )
        self.directory_path = Text(col={"sm": 8})

        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result
        )
        self.page.overlay.append(self.get_directory_dialog)
        self.directory_path = Text(col={"sm": 8})
        self.create_buttons()

        # Passes self.check_settings_complete() so that the child control
        # text fields can turn off the Save button
        self.settings_fields = TestSettingsLayout(
            self.page,
            self.directory_path,
            check_complete=self.check_settings_complete,
        )

        self.trial_table = None

        self.make_app_layout()

        self.page.update()

    def make_app_layout(self):
        self.settings_title = Text(
            "Experiment Settings", style=ft.TextThemeStyle.HEADLINE_LARGE
        )

        self.trials_title = Text(
            "Trial Order", style=ft.TextThemeStyle.HEADLINE_LARGE
        )

        self.progress_title = Text(
            "Experiment Progress", style=ft.TextThemeStyle.HEADLINE_LARGE
        )

        self.directory_prompt = Text(
            "Select experiment folder to save solenoid info"
        )

        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.window_width = 600
        self.page.window_height = 2000
        # self.page.window_resizable = False
        self.pick_directory_layout = ft.ResponsiveRow(
            [
                self.pick_directory_btn,
                self.directory_path,
            ]
        )

        self.save_reset_buttons = ft.ResponsiveRow(
            [
                self.randomize_option,
                self.save_settings_btn,
                self.reset_settings_btn,
            ]
        )

        self.randomize_start_buttons = ft.Row()

        self.app_layout = Column(
            width=600,
            controls=[
                self.settings_title,
                self.directory_prompt,
                self.pick_directory_layout,
                self.settings_fields,
                self.save_reset_buttons,
                # self.experiment_info_layout,
                # self.randomize_start_buttons,
            ],
        )

    # Open directory dialog
    def get_directory_result(self, e: FilePickerResultEvent):
        self.directory_path.value = e.path if e.path else "Cancelled!"
        self.directory_path.update()
        self.check_settings_complete()

    def save_clicked(self, e):
        now_date = datetime.datetime.now()

        self.animal_id = self.settings_fields.animal_id.text_field.value
        self.roi = self.settings_fields.roi.text_field.value
        self.date = now_date.strftime("%y%m%d")
        self.num_odors = int(self.settings_fields.num_odors.value)
        self.num_trials = int(self.settings_fields.num_trials.text_field.value)
        self.odor_duration = int(
            self.settings_fields.odor_duration.text_field.value
        )
        self.time_btw_odors = int(
            self.settings_fields.time_btw_odors.text_field.value
        )

        self.settings_dict = {
            "dir_path": self.directory_path.value,
            "mouse": self.animal_id,
            "roi": self.roi,
            "date": self.date,
            "num_odors": self.num_odors,
            "num_trials": self.num_trials,
            "odor_duration": self.odor_duration,
            "time_btw_odors": self.time_btw_odors,
            "randomize_trials": self.randomize_option.value,
        }
        self.save_settings_btn.disabled = True
        self.pick_directory_btn.disabled = True
        self.randomize_option.disabled = True

        self.settings_fields.disable_settings_fields(disable=True)

        # self.experiment_info_layout = ExperimentInfoLayout(
        #     self.page,
        #     self.randomize_option,
        #     self.num_trials,
        #     self.num_odors,
        #     reset=False,
        # )

        # Adds trial order table
        self.trial_table = TrialOrderTable(
            self.page,
            self.randomize_option.value,
            self.num_trials,
            self.num_odors,
            reset=False,
        )

        self.make_rand_start_buttons()

        if self.randomize_option.value is True:
            self.randomize_start_buttons.controls = [
                self.randomize_button,
                self.start_button,
            ]
        else:
            self.randomize_start_buttons.controls = [
                self.start_button,
            ]

        self.app_layout.controls.extend(
            [
                ft.Divider(),
                self.trials_title,
                self.trial_table,
                self.randomize_start_buttons,
            ]
        )

        self.update()

    def reset_clicked(self, e):
        self.directory_path.value = None
        self.randomize_option.value = True
        self.randomize_option.disabled = False
        self.settings_fields.reset_settings_clicked(e)
        self.check_settings_complete(e)
        self.pick_directory_btn.disabled = False

        if self.trial_table in self.app_layout.controls:
            self.app_layout.controls.remove(self.trial_table)

        if self.randomize_start_buttons in self.app_layout.controls:
            self.app_layout.controls.remove(self.randomize_start_buttons)

        self.update()

    def check_settings_complete(self, e=None):
        if (
            ""
            in [
                self.settings_fields.animal_id.text_field.value,
                self.settings_fields.roi.text_field.value,
                self.settings_fields.num_odors.value,
                self.settings_fields.num_trials.text_field.value,
                self.settings_fields.odor_duration.text_field.value,
                self.settings_fields.time_btw_odors.text_field.value,
            ]
            or self.settings_fields.num_odors.value is None
            or self.directory_path.value is None
            or self.directory_path.value == "Cancelled!"
        ):
            self.save_settings_btn.disabled = True

        else:
            self.save_settings_btn.disabled = False

        self.update()

    def randomize_trials_again(self, e):
        self.trial_table.randomize_trials(repeat=True, e=None)
        self.update()

    def start_clicked(self, e):
        self.reset_settings_btn.disabled = True
        self.randomize_button.disabled = True
        self.start_button.disabled = True

        self.save_solenoid_info()

        self.exp_progress_layout = ExperimentProgressLayout(self.page)
        self.app_layout.controls.extend(
            [ft.Divider(), self.progress_title, self.exp_progress_layout]
        )
        self.update()

    def save_solenoid_info(self):
        csv_name = (
            f"{self.date}_{self.animal_id}_ROI{self.roi}_solenoid_order.csv"
        )

        path = os.path.join(self.directory_path.value, csv_name)

        self.trial_table.trials_df.to_csv(
            path, header=["Odor #"], index_label="Trial"
        )

        self.page.snack_bar.content.value = (
            f"Solenoid info saved to {csv_name} in experiment directory."
        )
        self.page.snack_bar.open = True
        self.page.update()

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
            on_click=self.save_clicked,
            col={"sm": 4},
            disabled=True,
        )

        self.reset_settings_btn = ElevatedButton(
            "Reset Settings",
            icon=icons.REFRESH_ROUNDED,
            on_click=self.reset_clicked,
            col={"sm": 4},
            disabled=False,
        )

    def make_rand_start_buttons(self):
        self.start_button = ElevatedButton(
            "Start Experiment!!!!", on_click=self.start_clicked
        )

        if self.randomize_option.value is True:
            self.randomize_button = ElevatedButton(
                "Randomize Again",
                on_click=self.randomize_trials_again,
            )

    def build(self):
        return self.app_layout


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"
        app = OdorDeliveryApp(page)

        page.add(app)
        page.update()

    ft.app(target=main)
