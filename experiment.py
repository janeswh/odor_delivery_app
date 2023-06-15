import flet as ft
from flet import (
    UserControl,
    Column,
    Text,
)

from arduino_functions import ArduinoSession


class ExperimentProgressLayout(UserControl):
    def __init__(self, page, settings, odor_sequence):
        super().__init__()
        self.page = page
        self.settings = settings
        self.odor_sequence = odor_sequence

        # self.started_text = Text("Experiment in progress...")

        # Progress bar
        self.progress_bar = ft.ProgressBar(width=600)
        # Progress bar text
        self.progress_bar_text = Text()
        self.pb_column = Column([self.progress_bar_text, self.progress_bar])

        self.layout = Column(
            controls=[
                self.pb_column,
            ]
        )

        # self.get_arduino_layout()

    def get_arduino_layout(self):
        self.arduino_display = ArduinoSession(
            self.page,
            self.settings,
            self.odor_sequence,
            self.progress_bar,
            self.progress_bar_text,
        )

        self.layout.controls.append(self.arduino_display)

    def build(self):
        # self.layout = Column(controls=[self.pb_column, self.arduino_display])

        return self.layout
