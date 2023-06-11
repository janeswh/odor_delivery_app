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


# class SettingsLayout:
class SettingsLayout(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.settings_dict = None
        self.saved_click = False
        self.experiment_info_layout = Container()

        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result
        )
        self.directory_path = Text(col={"sm": 8})
        page.overlay.append(self.get_directory_dialog)

        self.create_settings_fields()
        self.arrange_settings_fields()
        self.create_settings_layout()

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
        self.page_title = Text(
            "Delivery Settings", style=ft.TextThemeStyle.DISPLAY_MEDIUM
        )
        self.directory_prompt = Text(
            "Select experiment folder to save solenoid info"
        )

        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.window_width = 600
        self.page.window_height = 600
        # page.window_resizable = False

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

        self.update()

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
        self.disable_settings_fields(disable=True)

        self.experiment_info_layout.content = ExperimentInfoLayout(
            self.page,
            self.randomize_option,
            self.num_trials.text_field.value,
            self.num_odors.value,
            reset=False,
        )

        self.update()

    def reset_settings_clicked(self, e):
        self.directory_path.value = None
        self.settings_dict = None
        self.animal_id.reset()
        self.roi.reset()
        self.num_odors.value = ""
        self.num_trials.reset()
        self.odor_duration.reset()
        self.time_btw_odors.reset()
        self.randomize_option.value = True

        self.check_settings_complete(e)
        self.disable_settings_fields(disable=False)

        self.experiment_info_layout.content = None
        self.update()

    def disable_settings_fields(self, disable):
        self.pick_directory_btn.disabled = disable
        self.animal_id.disabled = disable
        self.roi.disabled = disable
        self.num_odors.disabled = disable
        self.num_trials.disabled = disable
        self.odor_duration.disabled = disable
        self.time_btw_odors.disabled = disable
        self.randomize_option.disabled = disable

    def build(self):
        print("SettingsLayout build()")

        return ft.Column(
            width=600,
            controls=[
                self.page_title,
                self.directory_prompt,
                self.row1,
                self.row2,
                self.row3,
                self.row4,
                self.experiment_info_layout,
            ],
        )


class TrialOrderTable(UserControl):
    def __init__(self, page, randomize, num_trials, num_odors, reset):
        super().__init__()
        self.page = page

        self.randomize = randomize
        self.exp_display_content = Container()

        if reset is False:
            self.num_trials = int(num_trials)
            self.num_odors = int(num_odors)

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
        self.trials_df = self.trials_df.T

    def display_trial_order(self):
        # Using simpledt package fixes the page.add(DataTable) issue
        # https://github.com/StanMathers/simple-datatable

        simplet_df = DataFrame(self.trials_df)
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


class ExperimentInfoLayout(UserControl):
    def __init__(self, page, randomize, num_trials, num_odors, reset):
        super().__init__()
        self.page = page
        self.randomize = randomize.value
        self.randomize_button = None
        self.experiment_started = False

        self.exp_display_content = Text("Experiment Info Title")

        if reset is False:
            self.num_trials = int(num_trials)
            self.num_odors = int(num_odors)
            self.trials_table = TrialOrderTable(
                self.page,
                self.randomize,
                self.num_trials,
                self.num_odors,
                reset=False,
            )
        if self.randomize is True:
            self.make_randomize_button()
        else:
            self.randomize_button = Container()

        self.start_button = ElevatedButton(
            "Start Experiment", on_click=self.start_experiment
        )

    def make_randomize_button(self):
        self.randomize_button = ElevatedButton(
            "Randomize Again", on_click=self.get_new_trials_table
        )

    def get_new_trials_table(self, e):
        self.trials_table.randomize_trials(repeat=True, e=None)
        self.update()

    def start_experiment(self, e):
        print("experiment started")
        self.experiment_started = True
        self.experiment_info_layout.controls = [Text("Exp started")]
        self.update()

    def build(self):
        self.experiment_info_layout = Column(
            controls=[
                self.trials_table,
                Row(controls=[self.randomize_button, self.start_button]),
            ]
        )
        return self.experiment_info_layout


class OdorDeliveryApp(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.page.title = "Odor Delivery App"

        # self.settings = SettingsLayout(self.page)
        self.settings = SettingsLayout(self.page)
        # self.page.add(self.settings.return_layout())

        self.page.update()

    def build(self):
        # self.app_layout = Container(
        #     content=Column(controls=[self.settings.return_layout])
        # )

        # return self.app_layout
        return self.settings


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"
        app = OdorDeliveryApp(page)

        page.add(app)
        page.update()

    ft.app(target=main)
