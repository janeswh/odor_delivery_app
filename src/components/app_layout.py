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


class OdorDeliveryApp(UserControl):
    """Contains the skeleton structure for the Odor Delivery App.

    The structure is populated with other UserControl classes for experiment
    settings fields, trial order display, and experiment progress.

    Attributes:
        csv_time (str): Timestamp for saving the csv file.
        page (ft.Page): The page that OdorDeliveryApp will be added to.
        directory_path (str): Location of the experimental folder.
        get_directory_dialog (ft.FilePicker): A control that prompts user to
            select directory location.
        settings_fields (ft.UserControl): A UserControl class that contains the
            settings field for experimental settings.
        trial_table (ft.UserControl): A UserControl class that contains the
            odor/trial order displayed in a table.
        divider1 (ft.Divider): A horizontal divider for layout purposes.
        divider2 (ft.Divider): A horizontal divider for layout purposes.
        arduino_session (ft.UserControl): A UserControl class containing the
            signals sent to the arduino and all relevant experiment displays.
    """

    def __init__(self, page: Page):
        """Initializes an instance of OdorDeliveryApp to be added to the main
        page of the app.

        Args:
            page: The page that OdorDeliveryApp will be added to.
        """

        super().__init__()
        # self.port = None
        self.csv_time = None
        self.page = page
        # self.upload_arduino()
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

        self.directory_path = Text(col={"sm": 8})

        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result,
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
            update_parent=self.update_trial_type_settings,
        )

        self.trial_table = None
        self.divider1 = ft.Divider()
        self.divider2 = ft.Divider()
        self.arduino_session = None
        self.make_app_layout()

        self.page.update()

    def upload_arduino(self):
        # Compiles and uploads arduino sketch

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
        self.settings_title = Text(
            "Experiment Settings", style=ft.TextThemeStyle.HEADLINE_LARGE
        )

        self.trials_title = Text("Trial Order", style=ft.TextThemeStyle.HEADLINE_LARGE)

        self.progress_title = Text(
            "Experiment Progress", style=ft.TextThemeStyle.HEADLINE_LARGE
        )

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

    def close_banner(self, e):
        self.page.banner.open = False
        self.page.update()

    # Open directory dialog
    def get_directory_result(self, e: FilePickerResultEvent):
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
        folder = os.path.basename(self.directory_path.value)
        self.date = folder.split("--")[0]
        self.animal_id = folder.split("--")[1].split("_")[0]
        self.roi = folder.split("_")[1]

    def save_clicked(self, e):
        self.get_session_info()

        self.panel_type = self.settings_fields.panel_type.value
        self.trial_type = self.settings_fields.trial_type.value
        self.odor_duration = int(self.settings_fields.odor_duration.text_field.value)

        # Initialize variables
        self.num_odors = None
        self.num_trials = None
        self.time_btw_odors = None
        self.single_odor = None

        if self.trial_type == "Multiple":
            self.num_odors = int(self.settings_fields.num_odors.value)
            self.num_trials = int(self.settings_fields.num_trials.text_field.value)
            self.time_btw_odors = int(
                self.settings_fields.time_btw_odors.text_field.value
            )
        elif self.trial_type == "Single":
            self.single_odor = int(self.settings_fields.single_odor.value)
            self.time_btw_odors = 10  # TODO: double-check this

        self.settings_dict = {
            "dir_path": self.directory_path.value,
            "mouse": self.animal_id,
            "roi": self.roi,
            "date": self.date,
            "panel_type": self.panel_type,
            "single_odor": self.single_odor,
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

        # Adds trial order table
        self.trial_table = TrialOrderTable(
            self.page,
            self.trial_type,
            self.single_odor,
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
                self.divider1,
                self.trials_title,
                self.trial_table,
                self.randomize_start_buttons,
            ]
        )

        self.update()

    def reset_clicked(self, e):
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
        # Clear residual settings from previous trial type selection
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
            in [
                self.settings_fields.num_odors.value,
                self.settings_fields.num_trials.text_field.value,
                self.settings_fields.time_btw_odors.text_field.value,
            ]
            or self.settings_fields.num_odors.value is None
        ):
            if self.settings_fields.trial_type.value == "Multiple":
                self.save_settings_btn.disabled = True
            else:
                self.save_settings_btn.disabled = False

        else:
            self.save_settings_btn.disabled = False

        self.update()

    def randomize_trials_again(self, e):
        self.trial_table.randomize_trials(repeat=True, e=None)
        self.update()

    def start_clicked(self, e):
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
        self.update()

        self.start_arduino_session()

    def start_arduino_session(self):
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
        self.reset_clicked(e)
        self.close_newexp_dlg(e)

    def prompt_new_exp(self):
        """
        Shows dialog informing user that experiment has finished.
        """
        self.exp_fin_dlg = ft.AlertDialog(
            modal=True,
            title=Text("Odor delivery completed."),
            content=Text("Reset settings for new experiment?"),
            actions=[
                ft.TextButton(
                    # "Yes", on_click=lambda x: self.close_dlg(reset=True)
                    "Yes",
                    on_click=self.new_exp_clicked,
                ),
                # ft.TextButton("Yes", on_click=self.close_dlg),
                ft.TextButton("No", on_click=self.close_newexp_dlg),
            ],
        )
        self.page.dialog = self.exp_fin_dlg
        self.exp_fin_dlg.open = True
        self.page.update()

    def close_newexp_dlg(self, e):
        self.exp_fin_dlg.open = False
        self.reset_settings_btn.disabled = False
        self.start_button.disabled = False
        self.update()
        self.page.update()

    def abort_clicked(self, e):
        """
        Shows dialog informing user that experiment has finished.
        """
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
        self.abort_exp_dlg.open = False
        self.reset_settings_btn.disabled = False
        self.update()
        self.page.update()

    def save_solenoid_info(self):
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
            "Start Experiment",
            on_click=self.start_clicked,
            icon=ft.icons.START_ROUNDED,
        )

        if self.randomize_option.value is True:
            self.randomize_button = ElevatedButton(
                "Randomize Again",
                icon=ft.icons.SHUFFLE_ROUNDED,
                on_click=self.randomize_trials_again,
            )

        self.abort_btn = ft.ElevatedButton(
            "Abort Experiment",
            icon=ft.icons.STOP_ROUNDED,
            bgcolor=ft.colors.TERTIARY_CONTAINER,
            color=ft.colors.TERTIARY,
            on_click=self.abort_clicked,
            # on_click=self.abort,
            col={"sm": 4},
            disabled=False,
        )

    def abort(self, e):
        self.abort_exp_dlg.open = False
        self.page.update()
        self.arduino_session.stop_threads.set()
        self.abort_btn.disabled = True
        self.reset_settings_btn.disabled = False
        self.start_button.disabled = False
        self.update()

    def build(self):
        return self.app_layout
