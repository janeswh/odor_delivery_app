"""Contains the TrialOrderTable class to generate and display the experiment 
trial + odor order info in the app layout."""

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
import pdb


class TrialOrderTable(UserControl):
    """Generates trial order based on experiment settings and displays the
    order in a table."""

    def __init__(
        self,
        page: ft.Page,
        trial_type: str,
        single_odor: int,
        randomize: bool,
        num_trials: int,
        num_odors: int,
        specf_odors: str
        # reset: bool,
    ):
        """Initializes an instance of the TrialOrderTable class.

        Args:
            page: The page that OdorDeliveryApp will be added to.
            trial_type: Multiple or Single trials.
            single_odor: Odor number to delivery for single trial experiments.
            randomize: Whether to shuffle trials.
            num_trials: Number of trials to run per odor.
            num_odors: Number of odors to deliver.
            specf_odors: Numbers of specific odors to deliver.
            reset:
        """

        super().__init__()

        #: ft.Page: The page that OdorDeliveryApp will be added to
        self.page = page

        #: str: Multiple or Single trials
        self.trial_type = trial_type

        #: int: Odor number to delivery for single trial experiments
        self.single_odor = single_odor

        #: bool: Whether to shuffle trials
        self.randomize = randomize

        #: ft.Container: Layout for displaying all trial order UI elements
        self.exp_display_content = Container()

        #: int: Number of trials to run per odor
        self.num_trials = num_trials

        #: int:Number of odors to deliver
        self.num_odors = num_odors

        # if specf_odors is not None:
        #         self.specf_odors = [int(odor) for odor in specf_odors.split(",")]

        #: list: Numbers of specific odors to deliver, int in a list
        self.specf_odors = specf_odors

        # if self.num_trials != "" and self.num_odors != "":
        self.make_nonrandom_trials()

        if self.trial_type != "Single":
            if self.num_trials is not None:
                if self.trial_type == "Multiple" and self.num_odors is not None:
                    if self.randomize is True:
                        self.randomize_trials(repeat=False)

                if (
                    self.trial_type == "Limited Multiple"
                    and self.specf_odors is not None
                ):
                    if self.randomize is True:
                        self.randomize_trials(repeat=False)

        self.make_trials_df()
        self.display_trial_order()

    def make_nonrandom_trials(self):
        """Generates trial odor order for non-shuffled experiments."""

        if self.trial_type == "Single":
            #: list: The entire sequence of odors for every trial.
            self.trials = [self.single_odor]
        elif self.trial_type == "Multiple":
            self.trials = list(range(1, self.num_odors + 1)) * self.num_trials
        elif self.trial_type == "Limited Multiple":
            self.trials = self.specf_odors * self.num_trials

        self.update()

    def randomize_trials(self, repeat: bool, e=None):
        """Randomizes trials.

        Args:
            repeat: Whether this is a repeat from pressing Randomize Again.
            e (event): on_click event from pressing Randomize Again.
        """

        random.shuffle(self.trials)

        if repeat is True:
            self.make_trials_df()
            self.display_trial_order()
            print("randomize_trials repeat called")

        self.update()

    def make_trials_df(self):
        """Puts odor trials into a DataFrame."""

        #: pd.DataFrame: Trials in a DataFrame.
        self.trials_df = pd.DataFrame(self.trials)
        self.trials_df.rename(index=lambda s: s + 1, inplace=True)

    def display_trial_order(self):
        """Displays the trial order in a table.

        Using simpledt package fixes the page.add(DataTable) issue
        https://github.com/StanMathers/simple-datatable
        """

        simplet_df = DataFrame(self.trials_df.T)  # simpledt class

        #: simpledt.DataFrame: Displays trials_df correctly on app
        self.simple_dt = simplet_df.datatable

        # Add Trial/Odor labels to table
        self.simple_dt.columns.insert(0, ft.DataColumn(ft.Text("Trial")))
        self.simple_dt.rows[0].cells.insert(0, ft.DataCell(content=Text("Odor")))

        self.simple_dt.column_spacing = 20
        self.simple_dt.heading_row_height = 25
        self.simple_dt.data_row_height = 40
        self.simple_dt.horizontal_lines = ft.border.BorderSide(
            2, ft.colors.ON_SECONDARY
        )
        self.simple_dt.vertical_lines = ft.border.BorderSide(1, ft.colors.ON_SECONDARY)

        self.simple_dt.heading_row_color = ft.colors.SECONDARY_CONTAINER
        # self.simple_dt.heading_text_style = ft.TextStyle(
        #     color=ft.colors.OUTLINE_VARIANT
        # )

        self.exp_display_content.content = Row(
            controls=[self.simple_dt], scroll="always"
        )

        self.update()

    def build(self):
        # self.info_layout = Container(content=self.exp_display_content)

        # return self.info_layout
        return self.exp_display_content
