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
    ):
        super().__init__()

        self.hello = "hello"

        self.textfield_dict = {
            "Animal ID": {"value": ""},
            "ROI": {"value": ""},
            "# Trials/odor": {"value": ""},
            "Odor duration (s)": {"value": 1},
            "Time between odors (s)": {"value": "10"},
        }

        self.text_field = TextField(
            value=self.textfield_dict[label]["value"],
            label=label,
            on_change=None,
            col={"sm": 4},
        )

        if label == "Animal ID":
            self.text_field.hint_text = "e.g. 123456-1-2"

    def build(self):
        return self.text_field


class OdorDeliveryApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "Odor Delivery App"

        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result
        )
        self.directory_path = Text(col={"sm": 8})
        page.overlay.append(self.get_directory_dialog)

        self.create_settings_layout()
        self.page.add(self.main_layout)
        self.page.update()

    # def did_mount(self):
    #     self.get_directory_dialog = FilePicker(
    #         on_result=self.get_directory_result
    #     )

    #     self.directory_path = Text(col={"sm": 8})
    #     print("hello")

    def create_settings_layout(self):
        self.main_layout = Column()

        self.create_buttons()

        self.main_layout.controls = [self.pick_directory_btn]

    def create_buttons(self):
        self.pick_directory_btn = ElevatedButton(
            "Open directory",
            icon=icons.FOLDER_OPEN,
            col={"sm": 4},
            on_click=lambda _: self.get_directory_dialog.get_directory_path(),
            # disabled=self.page.web,
        )

    # Open directory dialog
    def get_directory_result(self, e: FilePickerResultEvent):
        self.directory_path.value = e.path if e.path else "Cancelled!"
        self.directory_path.update()
        # self.check_settings_complete(e)

    # def build(self):
    #     print("hello2")

    #     self.create_settings_layout()
    #     return self.main_layout


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"

        app = OdorDeliveryApp(page)
        page.update()
        # page.add(app)

    ft.app(target=main)
