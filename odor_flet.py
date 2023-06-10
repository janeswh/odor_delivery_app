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

import pandas as pd
import datetime
import random
import serial
import os
import pdb


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


# class SaveSettingsButton(UserControl):
#     def __init__(self, settings_dict):
#         super().__init__()
#         self.settings_dict = settings_dict

#     def save_settings(self, e):
#         now_date = datetime.datetime.now()
#         self.settings_dict = {
#             "dir_path": self.directory_path,
#             "mouse": self.animal_id,
#             "roi": self.roi,
#             "date": now_date.strftime("%y%m%d"),
#             "num_odors": self.num_odors,
#             "num_trials": self.num_trials,
#             "odor_duration": self.odor_duration,
#             "time_btw_odors": self.time_btw_odors,
#             "randomize_trials": self.randomize_option,
#         }

#     def build(self):
#         # self.button = ElevatedButton(
#         #     "Save Settings",
#         #     icon=icons.SAVE_ALT_ROUNDED,
#         #     on_click=self.save_settings,
#         #     col={"sm": 4},
#         #     disabled=True,
#         # )
#         return ElevatedButton(
#             "Save Settings",
#             icon=icons.SAVE_ALT_ROUNDED,
#             on_click=self.save_settings,
#             col={"sm": 4},
#             disabled=True,
#         )


class SettingsLayout:
    def __init__(self, page: Page):
        self.page = page
        self.settings_dict = None
        self.saved_click = False
        self.experiment_info_layout = None

        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result
        )
        self.directory_path = Text(col={"sm": 8})
        page.overlay.append(self.get_directory_dialog)

        self.create_settings_fields()
        self.arrange_settings_fields()
        self.create_settings_layout()
        self.page.update()

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

        self.create_buttons()

    # Arranges setting fields in rows
    def arrange_settings_fields(self):
        self.row1 = ft.ResponsiveRow(
            [
                self.pick_directory_btn,
                self.directory_path,
            ]
        )

        self.row2 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.animal_id]),
                Column(col={"sm": 4}, controls=[self.roi]),
                Column(col={"sm": 4}, controls=[self.num_odors]),
            ]
        )

        self.row3 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.odor_duration]),
                Column(col={"sm": 4}, controls=[self.time_btw_odors]),
                Column(col={"sm": 4}, controls=[self.num_trials]),
            ]
        )

        self.row4 = ft.ResponsiveRow(
            [
                self.randomize_option,
                self.save_settings_btn,
                self.reset_settings_btn,
            ]
        )

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

        self.reset_settings_btn = ElevatedButton(
            "Reset Settings",
            icon=icons.SAVE_ALT_ROUNDED,
            on_click=self.reset_settings_clicked,
            col={"sm": 4},
            disabled=False,
        )

        # self.save_settings_btn = SaveSettingsButton(self.settings_dict)

    def create_settings_layout(self):
        page_title = Text(
            "Delivery Settings", style=ft.TextThemeStyle.DISPLAY_MEDIUM
        )
        directory_prompt = Text(
            "Select experiment folder to save solenoid info"
        )

        # # Empty space for trial order
        # self.raw_trials_table = ft.DataTable()
        # self.trials_table = [self.raw_trials_table]
        # self.trials_table_row = ft.Container(ft.Row(self.trials_table))

        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.window_width = 600
        self.page.window_height = 600
        # page.window_resizable = False

        self.settings_layout = ft.Column(
            width=600,
            controls=[
                page_title,
                directory_prompt,
                self.row1,
                self.row2,
                self.row3,
                self.row4,
                # self.trials_table_row,
            ],
        )

    # Open directory dialog
    def get_directory_result(self, e: FilePickerResultEvent):
        self.directory_path.value = e.path if e.path else "Cancelled!"
        self.directory_path.update()
        self.check_settings_complete(e)

    # Checks whether all settings have been entered and create save button
    def check_settings_complete(self, e):
        if (
            ""
            in [
                self.directory_path.value,
                self.animal_id.text_field.value,
                self.roi.text_field.value,
                self.num_odors.value,
                self.num_trials.text_field.value,
                self.odor_duration.text_field.value,
                self.time_btw_odors.text_field.value,
            ]
            or self.num_odors.value is None
            or self.directory_path.value is None
        ):
            self.save_settings_btn.disabled = True

        else:
            self.save_settings_btn.disabled = False

        self.page.update()

    def save_settings_clicked(self, e):
        now_date = datetime.datetime.now()
        self.settings_dict = {
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
        self.save_settings_btn.disabled = True

        if self.experiment_info_layout is not None:
            self.page.controls.remove(self.experiment_info_layout)

        self.experiment_info_layout = ExperimentInfoLayout(
            self.page,
            self.randomize_option,
            self.num_trials.text_field.value,
            self.num_odors.value,
            reset=False,
        )
        self.page.add(self.experiment_info_layout)
        # self.page.add(ExperimentInfoLayout(self.page, self.randomize_option))

        self.page.update()

    def reset_settings_clicked(self, e):
        self.settings_dict = None
        self.animal_id.reset()
        self.roi.reset()
        self.num_odors.value = ""
        self.num_trials.reset()
        self.odor_duration.reset()
        self.time_btw_odors.reset()
        self.randomize_option.value = True

        # # finds matching type of controls currently on the page and replaces
        # # with new ExperimentInfoLayout
        # controls_type = [type(control) for control in self.page.controls]
        # control_i = [
        #     i
        #     for i, control in enumerate(controls_type)
        #     if issubclass(controls_type[i], ExperimentInfoLayout)
        # ]

        # Need to make a new ExperimentInfoLayout to replace old one, not sure
        # why updating old instance with unsaved() doesn't work

        if self.experiment_info_layout is not None:
            self.page.controls.remove(self.experiment_info_layout)

        self.experiment_info_layout = ExperimentInfoLayout(
            self.page,
            self.randomize_option,
            self.num_trials.text_field.value,
            self.num_odors.value,
            reset=True,
        )
        self.experiment_info_layout.unsaved()

        # self.page.controls[control_i[0]] = self.experiment_info_layout
        self.page.add(self.experiment_info_layout)
        self.page.update()

    def return_layout(self):
        return self.settings_layout


class ExperimentInfoLayout(UserControl):
    def __init__(self, page, randomize, num_trials, num_odors, reset):
        super().__init__()
        self.page = page
        self.randomize = randomize

        self.exp_display_text = "Initial save"

        if reset is False:
            self.num_trials = int(num_trials)
            self.num_odors = int(num_odors)

            if self.num_trials != "" and self.num_odors != "":
                self.randomize_trials()
                self.make_trials_df()
                self.display_trial_order()

    def randomize_trials(self):
        self.trials = list(range(1, self.num_odors + 1)) * self.num_trials
        random.shuffle(self.trials)

    def make_trials_df(self):
        """
        Puts odor trials into a df
        """
        trial_labels = list(range(1, len(self.trials) + 1))
        self.trials_df = pd.DataFrame(
            {"Trial": trial_labels, "Odor #": self.trials}
        )

    def display_trial_order(self):
        self.raw_trials_table = ft.DataTable()
        self.trials_table = [self.raw_trials_table]
        self.trials_df = self.trials_df.T

        for trials_num in range(len(self.trials_df.columns)):
            self.raw_trials_table.columns.append(
                ft.DataColumn(ft.Text(self.trials_df.columns[trials_num]))
            )
        self.raw_trials_table.rows.append(
            ft.DataRow(cells=self.trials_df.loc["Odor #"].tolist())
        )
        self.trials_table[0] = self.raw_trials_table

        print("table made")

    def post_save(self):
        self.exp_display_text = "Saved"
        self.update()

    def unsaved(self):
        self.exp_display_text = "Settings not saved"
        print("settings not saved should be triggered")

        self.update()

    def build(self):
        # self.info_layout = Column(controls=[Text(self.exp_display_text)])
        self.info_layout = Text(self.exp_display_text)
        # self.info_layout = self.raw_trials_table

        return self.info_layout


# class OdorDeliveryApp:
#     def __init__(self, page: Page):
#         self.page = page
#         self.page.title = "Odor Delivery App"

#         self.settings = SettingsLayout(page)

#         self.page.add(self.settings.return_layout())
#         self.page.add(Text("hello"))

#         self.page.add(
#             ExperimentInfoLayout(page, self.settings.randomize_option.value)
#         )

#         self.page.update()

#         if self.settings.saved_click == True:
#             print("app sees setting saved")

#         self.page.update()

#     def check_saved_clicked(self):
#         self.saved = self.settings.check_saved_clicked()


class OdorDeliveryApp(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.page.title = "Odor Delivery App"

        self.settings = SettingsLayout(self.page)
        self.page.add(self.settings.return_layout())

        self.page.add(Text("odor control init"))

        self.page.update()

    def build(self):
        # self.app_layout = Container(
        #     content=Column(controls=[self.settings.return_layout])
        # )

        self.app_layout = Text("odor delivery control")
        return self.app_layout


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"
        app = OdorDeliveryApp(page)

        page.add(app)
        page.update()

    ft.app(target=main)
