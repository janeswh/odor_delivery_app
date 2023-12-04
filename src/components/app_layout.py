"""Contains the OdorDeliveryApp class to contain the basic UI for the app."""

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

import os
import pdb
from datetime import datetime

from components.settings_layout import SettingsLayout
from components.trial_order import TrialOrderTable
from components.arduino_functions import ArduinoSession
from components.utils import resolve_path

import pyduinocli
from threading import Thread
import re


class OdorDeliveryApp(UserControl):
    """Contains the skeleton structure for the Odor Delivery App.

    The structure is populated with other UserControl classes for experiment
    settings fields, trial order display, and experiment progress.
    """

    def __init__(self, page: Page):
        """Initializes an instance of OdorDeliveryApp to be added to the main
        page of the app.

        Args:
            page: The page that OdorDeliveryApp will be added to.
        """

        super().__init__()
        # self.port = None

        #: str: Timestamp for saving the csv file
        self.csv_time = None

        #: ft.Page: The page that OdorDeliveryApp will be added to
        self.page = page

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Snack bar init"), bgcolor=ft.colors.SECONDARY
        )

        self.page.banner = ft.Banner(
            bgcolor=ft.colors.TERTIARY_CONTAINER,
            leading=ft.Icon(
                ft.icons.WARNING_AMBER_ROUNDED,
                color=ft.colors.TERTIARY,
                size=40,
            ),
            content=ft.Text(
                "Please make sure the selected experiment folder is named "
                "in the correct format of YYMMDD--123456-7-8_ROIX where "
                "123456-7-8 is the animal ID, and X is the one-digit ROI number."
            ),
            actions=[
                ft.TextButton("OK", on_click=self.close_banner),
            ],
            force_actions_below=True,
        )

        #: ft.Text: Flet Text object containing location of the
        # experimental folder
        self.directory_path = Text(col={"sm": 8})

        #: ft.FilePicker: A control that prompts user to select directory
        # location
        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result,
        )
        self.page.overlay.append(self.get_directory_dialog)
        self.create_buttons()

        # Passes self.check_settings_complete() so that the child control
        # text fields can turn off the Save button

        #: ft.UserControl): A UserControl class that contains the settings
        # field for experimental settings
        self.settings_fields = SettingsLayout(
            self.page,
            self.directory_path,
            check_complete=self.check_settings_complete,
            update_parent=self.update_trial_type_settings,
        )

        #: ft.UserControl: A UserControl class that contains the odor/trial
        # order displayed in a table
        self.trial_table = None

        #: ft.Divider: A horizontal divider for layout purposes
        self.divider1 = ft.Divider()

        #: ft.Divider: A horizontal divider for layout purposes
        self.divider2 = ft.Divider()

        #: ft.UserControl: Layout containing the signals sent to the arduino
        # and all relevant experiment displays
        self.arduino_session = None

        self.make_app_layout()
        self.page.update()

    def upload_arduino(self):
        """Compiles and uploads arduino sketches.

        Uploads blank sketch to whichever port isn't being used.
        """

        self.page.snack_bar.content.value = "Uploading sketch to Arduino..."
        self.page.snack_bar.open = True
        self.page.update()

        arduino_cli_path = resolve_path("resources/arduino-cli.exe")
        arduino_instance = pyduinocli.Arduino(arduino_cli_path)
        fqbn = "arduino:avr:mega"

        # Define ports and arduino sketches
        arduino_ports_dict = {
            "1%": {"active": "COM8", "inactive": "COM7"},
            "10%": {"active": "COM7", "inactive": "COM8"},
        }

        arduino_sketch_dict = {
            "active": "arduino_sketch",
            "inactive": "blank_sketch",
        }

        # Selects port based on odor panel type and uploads sketches
        for port_type in arduino_ports_dict[self.panel_type].keys():
            sketch_path = resolve_path(arduino_sketch_dict[port_type])
            arduino_instance.compile(fqbn=fqbn, sketch=sketch_path)
            arduino_instance.upload(
                fqbn=fqbn,
                sketch=sketch_path,
                port=arduino_ports_dict[self.panel_type][port_type],
            )

    def make_app_layout(self):
        """Sets up the initial layout of the odor delivery app."""

        #: ft.Text: Header for the Settings layout
        self.settings_title = Text(
            "Experiment Settings", style=ft.TextThemeStyle.HEADLINE_LARGE
        )

        #: ft.Text: Header for the Trial Order layout
        self.trials_title = Text("Trial Order", style=ft.TextThemeStyle.HEADLINE_LARGE)

        #: ft.Text: Header for the Progress layout
        self.progress_title = Text(
            "Experiment Progress", style=ft.TextThemeStyle.HEADLINE_LARGE
        )

        #: ft.Column: Layout containing prompts to pick directory
        self.directory_prompt = Column(
            controls=[
                Text("Select experiment folder to save solenoid info"),
                Text("Folder should be named in the format YYMMDD--123456-7-8_ROIX"),
            ]
        )

        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.window_width = 600
        self.page.window_height = 900
        self.page.window_resizable = False

        #:  ft.ResponsiveRow: Layout containing directory picker UI elements
        self.pick_directory_layout = ft.ResponsiveRow(
            [
                self.pick_directory_btn,
                self.directory_path,
            ]
        )

        #: ft.ResponsiveRow: Layout containing buttons
        self.save_reset_buttons = ft.ResponsiveRow(
            [
                self.randomize_option,
                self.save_settings_btn,
                self.reset_settings_btn,
            ]
        )

        #: ft.Row: Layout containing buttons
        self.randomize_start_buttons = ft.Row()

        #: ft.Column: Layout for the whole app
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

    def close_banner(self, e):
        """Closes the error message banner.

        Args:
            e (event): on_click event from button clicking.
        """

        self.page.banner.open = False
        self.page.update()

    def get_directory_result(self, e: FilePickerResultEvent):
        """Open directory picker dialog.

        Args:
            e (event): on_result event with directory path from the FilePicker.
        """

        self.directory_path.value = e.path

        try:
            self.get_session_info()
            self.page.banner.open = False
        except TypeError:
            self.directory_path.value = "Cancelled!"
            self.page.banner.open = False

        except IndexError:
            if self.directory_path.value == "":
                self.directory_path.value = "Cancelled!"
                self.page.banner.open = False
            else:
                self.page.banner.open = True
                self.directory_path.value = None

        self.page.update()
        self.directory_path.update()
        self.check_settings_complete()

    def get_session_info(self):
        """Parses the directory folder for experiment session info."""

        folder = os.path.basename(self.directory_path.value)

        #: str: Date of the experiment
        self.date = folder.split("--")[0]

        #: str: Animal ID of the experiment
        self.animal_id = folder.split("--")[1].split("_")[0]

        #: str: ROI of the experiment
        self.roi = folder.split("_")[1]

    def save_settings(self):
        """Saves the user-input experiment settings to a dict."""

        #: str: Whether odor panel is 1% or 10%
        self.panel_type = self.settings_fields.panel_type.value

        #: str: Multiple or Single trials
        self.trial_type = self.settings_fields.trial_type.value

        #: int: Duration of odor in s
        self.odor_duration = int(self.settings_fields.odor_duration.text_field.value)

        #: int: Number of odors to deliver
        self.num_odors = None

        #: list: Specific odors to deliver
        self.specf_odors = None

        #: str: Number of trials to run per odor
        self.num_trials = None

        #: int: Time in s between odors
        self.time_btw_odors = None

        # int: Odor number to delivery for single trial experiments
        self.single_odor = None

        if self.trial_type == "Single":
            self.single_odor = int(self.settings_fields.single_odor.value)
            self.time_btw_odors = 10  # TODO: double-check this

        elif self.trial_type == "Multiple" or self.trial_type == "Limited Multiple":
            self.num_trials = int(self.settings_fields.num_trials.text_field.value)
            self.time_btw_odors = int(
                self.settings_fields.time_btw_odors.text_field.value
            )

            if self.trial_type == "Multiple":
                self.num_odors = int(self.settings_fields.num_odors.value)
            elif self.trial_type == "Limited Multiple":
                self.specf_odors = [
                    int(odor)
                    for odor in self.settings_fields.specf_odors.text_field.value.split(
                        ","
                    )
                ]

        #: dict: All experiment settings entered from settings fields
        self.settings_dict = {
            "dir_path": self.directory_path.value,
            "mouse": self.animal_id,
            "roi": self.roi,
            "date": self.date,
            "panel_type": self.panel_type,
            "single_odor": self.single_odor,
            "num_odors": self.num_odors,
            "specific_odors": self.specf_odors,
            "num_trials": self.num_trials,
            "odor_duration": self.odor_duration,
            "time_btw_odors": self.time_btw_odors,
            "randomize_trials": self.randomize_option.value,
        }

    def check_specf_odors_format(self):
        """Checks whether the odors entered for Limited Multiple trial are
        entered in the correct format.

        Returns:
            Bool of whether odors are formatted correctly

        """
        correct_format = None

        if self.settings_fields.specf_odors.text_field.value:
            pattern = re.compile("^[1-8](,[1-8])*$")
            if pattern.match(self.settings_fields.specf_odors.text_field.value) is None:
                self.settings_fields.specf_odors.text_field.error_text = (
                    "Check odor input"
                )
                correct_format = False
            else:
                self.settings_fields.specf_odors.text_field.error_text = ""
                correct_format = True

            self.settings_fields.specf_odors.text_field.update()

        return correct_format

    def save_clicked(self, e):
        """Saves settings and populates app layout after clicking Save button.

        Args:
            e (event): on_result event from clicking Save Settings button.
        """

        if self.settings_fields.trial_type.value == "Limited Multiple":
            specf_format = self.check_specf_odors_format()

        if self.settings_fields.trial_type.value != "Limited Multiple" or (
            self.settings_fields.trial_type.value == "Limited Multiple"
            and specf_format is True
        ):
            self.get_session_info()
            self.save_settings()

            self.save_settings_btn.disabled = True
            self.pick_directory_btn.disabled = True
            self.randomize_option.disabled = True
            self.settings_fields.disable_settings_fields(disable=True)

            self.trial_table = TrialOrderTable(
                self.page,
                self.trial_type,
                self.single_odor,
                self.randomize_option.value,
                self.num_trials,
                self.num_odors,
                self.specf_odors
                # reset=False,
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
                    self.divider1,
                    self.trials_title,
                    self.trial_table,
                    self.randomize_start_buttons,
                ]
            )

        self.update()

    def reset_clicked(self, e):
        """Resets settings and resets button/input states, as well as clearing
        outdated information from app layout.

        Args:
            e (event): on_result event from clicking Reset Settings button.
        """

        self.directory_path.value = None
        self.settings_dict = None
        self.randomize_option.value = True
        self.randomize_option.disabled = False
        self.settings_fields.reset_settings_clicked(e)
        self.check_settings_complete(e)
        self.pick_directory_btn.disabled = False

        for control in [
            self.divider1,
            self.trials_title,
            self.trial_table,
            self.randomize_start_buttons,
            self.divider2,
            self.progress_title,
            self.arduino_session,
        ]:
            if control in self.app_layout.controls:
                self.app_layout.controls.remove(control)

        self.update_trial_type_settings(e)
        self.update()

    def update_trial_type_settings(self, e):
        """Clears residual settings from previous trial type selection

        Args:
            e (event): on_result event from clicking Reset Settings button.
        """

        self.settings_fields.reset_settings_clicked(e, keep_paneltype=True)

        self.settings_fields.controls[0].controls = [
            self.settings_fields.row1,
            self.settings_fields.row2,
        ]

        self.settings_fields.update()

        if self.settings_fields.trial_type.value == "Single":
            self.randomize_option.value = False
            self.randomize_option.disabled = True
        elif self.settings_fields.trial_type.value == "Multiple":
            self.randomize_option.value = True
            self.randomize_option.disabled = False

        self.update()

    def check_settings_complete(self, e=None):
        """Checks whether all settings fields have been filled out before
        allowing experiment to proceed.

        Args:
            e (event): on_result event from clicking Reset Settings button.
        """

        if (
            ""
            in [
                self.settings_fields.panel_type.value,
                self.settings_fields.odor_duration.text_field.value,
            ]
            or self.directory_path.value is None
            or self.directory_path.value == ""
            or self.directory_path.value == "Cancelled!"
        ):
            self.save_settings_btn.disabled = True

        elif (
            ""
            not in [
                # self.settings_fields.num_trials.text_field.value,
                self.settings_fields.odor_duration.text_field.value,
                self.settings_fields.time_btw_odors.text_field.value,
            ]
            # or self.settings_fields.num_odors.value is None
        ):
            if self.settings_fields.trial_type.value == "Single":
                self.save_settings_btn.disabled = False
            elif self.settings_fields.num_trials.text_field.value != "":
                if (
                    self.settings_fields.trial_type.value == "Multiple"
                    and self.settings_fields.num_odors.value != ""
                ):
                    self.save_settings_btn.disabled = False
                elif (
                    self.settings_fields.trial_type.value == "Limited Multiple"
                    and self.settings_fields.specf_odors.text_field.value != ""
                ):
                    self.save_settings_btn.disabled = False
            else:
                self.save_settings_btn.disabled = True

        else:
            self.save_settings_btn.disabled = True

        self.update()

    def randomize_trials_again(self, e):
        """Randomizes trial order again.

        Args:
            e (event): on_result event from clicking Randomize Again button.
        """

        self.trial_table.randomize_trials(repeat=True, e=None)
        self.update()

    def start_clicked(self, e):
        """Uploads arduino sketch and retrieves arduino session layout for app.
        Also saves the solenoid info to csv file.

        Args:
            e (event): on_result event from clicking Start Experiment button.
        """

        self.start_button.disabled = True
        self.reset_settings_btn.disabled = True
        if self.randomize_option.value is True:
            self.randomize_button.disabled = True
        self.abort_btn.disabled = False
        self.upload_arduino()
        self.csv_time = datetime.now().strftime("%y%m%d-%H%M%S")

        self.save_solenoid_info()

        for control in [
            self.divider2,
            self.progress_title,
            self.arduino_session,
        ]:
            if control in self.app_layout.controls:
                self.app_layout.controls.remove(control)

        self.arduino_session = ArduinoSession(
            self.panel_type,
            self.csv_time,
            self.page,
            self.settings_dict,
            self.trial_table.trials,
        )

        self.app_layout.controls.extend(
            [
                self.divider2,
                self.progress_title,
                self.arduino_session,
                # self.abort_btn,
            ]
        )

        self.update()
        self.arduino_session.arduino_layout.content.controls[2].controls.append(
            self.abort_btn
        )
        # self.update()  # Don't need this I think

        self.start_arduino_session()

    def start_arduino_session(self):
        """Starts the arduino session and sends signals to the arduino board
        in a threaded process.
        """

        if self.arduino_session.trig_signal is False:
            while (
                self.arduino_session.trig_signal is False
                and self.arduino_session.sequence_complete is False
                and not self.arduino_session.stop_threads.is_set()
            ):
                arduino_msg = self.arduino_session.get_arduino_msg()
                if "y" in arduino_msg:
                    self.arduino_session.trig_signal = True

                    thread = Thread(target=self.arduino_session.generate_arduino_str)
                    thread.start()
                    thread.join()

                    self.arduino_session.trig_signal = False

                    if not self.arduino_session.stop_threads.is_set():
                        self.prompt_new_exp()

                else:
                    pass

        if (
            self.arduino_session.trig_signal is False
            and self.arduino_session.sequence_complete is True
        ):
            self.arduino_session.close_port()
            # self.port = None

        self.abort_btn.disabled = True
        self.arduino_session.update()  # to show disabled button

    def new_exp_clicked(self, e):
        """Resets settings fields for new experiment.

        Args:
            e (event): on_result event from clicking Yes to reset settings for
            new experiments prompt.
        """

        self.reset_clicked(e)
        self.close_newexp_dlg(e)

    def prompt_new_exp(self):
        """Shows dialog informing user that experiment has finished."""

        #: ft.AlertDialog: Alert dialog upon experiment completion
        self.exp_fin_dlg = ft.AlertDialog(
            modal=True,
            title=Text("Odor delivery completed."),
            content=Text("Reset settings for new experiment?"),
            actions=[
                ft.TextButton("Yes", on_click=self.new_exp_clicked),
                ft.TextButton("No", on_click=self.close_newexp_dlg),
            ],
        )
        self.page.dialog = self.exp_fin_dlg
        self.exp_fin_dlg.open = True
        self.page.update()

    def close_newexp_dlg(self, e):
        """Closes dialog informing user that experiment has finished.

        Args:
            e (event): on_result event from clicking "No" on the prompt asking
            user to reset settings for new experiment.
        """

        self.exp_fin_dlg.open = False
        self.reset_settings_btn.disabled = False
        self.start_button.disabled = False
        self.update()
        self.page.update()

    def abort_clicked(self, e):
        """Shows dialog prompting user to confirm stopping the experiment.

        Args:
            e (event): on_result event from clicking Abort Experiment button.
        """

        #: ft.AlertDialog: Alert dialog upon stopping experiment
        self.abort_exp_dlg = ft.AlertDialog(
            modal=False,
            title=Text("Please confirm"),
            content=Text("Are you sure you want to stop the experiment?"),
            actions=[
                ft.TextButton(
                    "Yes",
                    on_click=self.abort,
                ),
                ft.TextButton("No", on_click=self.close_abort_dlg),
            ],
        )
        self.page.dialog = self.abort_exp_dlg
        self.abort_exp_dlg.open = True
        self.page.update()

    def close_abort_dlg(self, e):
        """Closes the confirm stopping experiment dialog.

        Args:
            e (event): on_result event from clicking No on the dialog
            confirming stopping the experiment.
        """

        self.abort_exp_dlg.open = False
        self.reset_settings_btn.disabled = False
        self.update()
        self.page.update()

    def save_solenoid_info(self):
        """Saves the solenoid order to a .csv file."""

        csv_name = (
            f"{self.date}_{self.animal_id}_{self.roi}_solenoid_order_"
            f"{self.csv_time}.csv"
        )

        path = os.path.join(self.directory_path.value, csv_name)

        # sort trial order info by odor #
        sorted_df = self.trial_table.trials_df.copy()
        sorted_df["Trial"] = range(1, len(sorted_df) + 1)
        sorted_df.columns = sorted_df.columns.astype(str)
        sorted_df.rename(columns={"0": f"Odor {self.panel_type}"}, inplace=True)
        sorted_df.sort_values(by=[f"Odor {self.panel_type}"], inplace=True)

        sorted_df.to_csv(path, index=False)

        self.page.snack_bar.content.value = (
            f"Solenoid info saved to {csv_name} in experiment directory."
        )
        self.page.snack_bar.open = True
        self.page.update()

    def create_buttons(self):
        """Creates the buttons used for Settings fields."""

        #: ft.ElevatedButton: Button to click to select directory
        self.pick_directory_btn = ElevatedButton(
            "Open directory",
            icon=icons.FOLDER_OPEN,
            col={"sm": 4},
            on_click=lambda _: self.get_directory_dialog.get_directory_path(
                # initial directory doesn't work yet - https://github.com/flet-dev/flet/issues/884
                # initial_directory="D:\\Jane"
            ),
            disabled=self.page.web,
        )

        #: ft.ElevatedButton: Randomize selector option
        self.randomize_option = ft.Switch(
            label="Shuffle trials", value=True, col={"sm": 4}
        )

        #: ft.ElevatedButton: Save Settings button
        self.save_settings_btn = ElevatedButton(
            "Save Settings",
            icon=icons.SAVE_ALT_ROUNDED,
            on_click=self.save_clicked,
            col={"sm": 4},
            disabled=True,
        )

        #: ft.ElevatedButton: Reset Settings button
        self.reset_settings_btn = ElevatedButton(
            "Reset Settings",
            icon=icons.REFRESH_ROUNDED,
            on_click=self.reset_clicked,
            col={"sm": 4},
            disabled=False,
        )

    def make_rand_start_buttons(self):
        """Creates the Start Experiment, Randomize Again, and Abort Experiment
        buttons.
        """

        #: ft.ElevatedButton: Start Experiment button
        self.start_button = ElevatedButton(
            "Start Experiment",
            on_click=self.start_clicked,
            icon=ft.icons.START_ROUNDED,
        )

        if self.randomize_option.value is True:
            #: ft.ElevatedButton: Randomize Again button
            self.randomize_button = ElevatedButton(
                "Randomize Again",
                icon=ft.icons.SHUFFLE_ROUNDED,
                on_click=self.randomize_trials_again,
            )

        #: ft.ElevatedButton: Abort Experiment button
        self.abort_btn = ElevatedButton(
            "Abort Experiment",
            icon=ft.icons.STOP_ROUNDED,
            bgcolor=ft.colors.TERTIARY_CONTAINER,
            color=ft.colors.TERTIARY,
            on_click=self.abort_clicked,
            col={"sm": 4},
            disabled=False,
        )

    def abort(self, e):
        """Aborts the experiment by stopping the arduino session and disabling
        relevant buttons in the UI.

        Args:
            e (event): on_result event from from clicking Yes on the dialog
            confirming stopping the experiment.
        """

        self.abort_exp_dlg.open = False
        self.page.update()
        self.arduino_session.stop_threads.set()
        self.abort_btn.disabled = True
        self.reset_settings_btn.disabled = False
        self.start_button.disabled = False
        self.update()

    def build(self):
        return self.app_layout
