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

        self.hello = "hello"

        self.textfield_dict = {
            "Animal ID": {"value": ""},
            "ROI": {"value": ""},
            "# Trials/odor": {"value": ""},
            "Odor duration (s)": {"value": "1"},
            "Time between odors (s)": {"value": "10"},
        }

        self.text_field = TextField(
            value=self.textfield_dict[label]["value"],
            label=label,
            on_change=on_change,
        )

        if label == "Animal ID":
            self.text_field.hint_text = "e.g. 123456-1-2"

    def build(self):
        return self.text_field


class SettingsLayout:
    def __init__(self, page: Page):
        self.page = page
        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result
        )
        self.directory_path = Text(col={"sm": 8})
        page.overlay.append(self.get_directory_dialog)

        self.create_settings_fields()
        row1, row2, row3, row4 = self.arrange_settings_fields()
        self.create_settings_layout(row1, row2, row3, row4)
        self.page.update()

    def create_settings_fields(self):
        self.main_layout = Column()

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
            # width=100,
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            alignment=ft.alignment.center,
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
        settings_r1 = ft.ResponsiveRow(
            [
                self.pick_directory_btn,
                self.directory_path,
            ]
        )

        settings_r2 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.animal_id]),
                Column(col={"sm": 4}, controls=[self.roi]),
                Column(col={"sm": 4}, controls=[self.num_odors]),
            ]
        )

        settings_r3 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.odor_duration]),
                Column(col={"sm": 4}, controls=[self.time_btw_odors]),
                Column(col={"sm": 4}, controls=[self.num_trials]),
            ]
        )

        settings_r4 = ft.ResponsiveRow(
            [self.randomize_option, self.save_settings_btn]
        )

        return settings_r1, settings_r2, settings_r3, settings_r4

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
            # on_click=self.save_settings_clicked,
            col={"sm": 4},
            disabled=True,
        )

    def create_settings_layout(self, row1, row2, row3, row4):
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
                row1,
                row2,
                row3,
                row4,
                # self.trials_table_row,
            ],
        )

        self.page.add(self.main_layout)

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

    def make_layout(self):
        self.create_settings_layout(row1, row2, row3, row4)
        self.page.update()


class OdorDeliveryApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "Odor Delivery App"
        self.page.add(Text("hello"))
        settings_layout = SettingsLayout(page)

        self.page.update()
        # pdb.set_trace()


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"

        app = OdorDeliveryApp(page)
        page.update()
        # page.add(app)

    ft.app(target=main)
