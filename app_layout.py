import flet as ft
from flet import (
    UserControl,
    Column,
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Text,
    icons,
)


import datetime

import os
import pdb

from settings_layout import SettingsLayout
from trial_order import TrialOrderTable
from experiment import ExperimentProgressLayout
from arduino_functions import ArduinoSession



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
        self.settings_fields = SettingsLayout(
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
        self.page.window_height = 800
        self.page.window_resizable = False
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

        # self.exp_progress_layout = Container()
        # self.exp_progress_layout = ExperimentProgressLayout(
        #     self.page, self.settings_dict, self.trial_table.trials
        # )

        self.exp_progress_layout = ArduinoSession(
            self.page,
            self.settings_dict,
            self.trial_table.trials,
        )

        self.app_layout.controls.extend(
            [ft.Divider(), self.progress_title, self.exp_progress_layout]
        )

        self.update()



        # self.exp_progress_layout.get_arduino_layout()


        self.exp_progress_layout.generate_arduino_str()

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
