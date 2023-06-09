import flet as ft
from flet import (
    UserControl,
    Row,
    Container,
    Text,
)

from simpledt import DataFrame
import pandas as pd
import random


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

        return self.info_layout
