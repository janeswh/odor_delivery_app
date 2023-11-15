"""Contains the SettingsFields and SettingsLayout classes to create the
Settings section of the app layout."""

import flet as ft
from flet import (
    UserControl,
    TextField,
    Column,
    Page,
)

import pdb


class SettingsFields(UserControl):
    """Creates settings field for each specific input with default values.

    Attributes:
        label: Label next to the text field.
        on_change (function): Callback function to run when field is changed.
        textfield_dict (dict): Contains labels with default values.
        text_field (ft.TextField): The actual text field object.
    """

    def __init__(
        self,
        label: str = "",
        on_change=None,
    ):
        """Initializes an instance of the SettingsField class."""

        super().__init__()
        self.label = label

        self.textfield_dict = {
            "Odor panel type": {
                "value": "",
            },
            "# Trials/odor": {"value": ""},
            "Odor duration (s)": {"value": "1"},
            "Time between odors (s)": {"value": "10"},
        }

        self.text_field = TextField(
            value=self.textfield_dict[self.label]["value"],
            label=label,
            on_change=on_change,
            border_color=ft.colors.SECONDARY_CONTAINER,
            border_width=1,
            focused_border_color=ft.colors.SURFACE_TINT,
            focused_border_width=2,
        )

        if self.label == "Animal ID":
            self.text_field.hint_text = "e.g. 123456-1-2"

    def reset(self):
        """Resets the text field to default value."""
        self.text_field.value = self.textfield_dict[self.label]["value"]
        # self.update()

    def build(self):
        return self.text_field


class SettingsLayout(UserControl):
    """Creates settings layout to be added to the main app.

    Attributes:
        page (ft.Page): The page that OdorDeliveryApp will be added to.
        directory_path (ft.Text): Flet Textt object containing location of the
                experimental folder.
        settings_dict (dict): Dict containing all the settings from the
            settings fields.
    """

    def __init__(
        self, page: Page, directory_path: ft.Text, check_complete, update_parent
    ):
        """Initializes an instance of SettingsLayout to be added to the main
        page of the app.

        Args:
            page: The page that OdorDeliveryApp will be added to.
            directory_path: Flet Textt object containing location of the
                experimental folder.
            check_complete: Callback function to run that checks whether all
                fields have been completed.
            update_parent: Callback function to clear residual settings from
                previous trial type selection.
        """

        super().__init__()

        self.page = page
        self.directory_path = directory_path
        self.settings_dict = None
        # self.saved_click = False

        self.create_settings_fields(check_complete, update_parent)
        self.arrange_settings_fields()

    def create_settings_fields(self, check_complete, update_parent):
        self.panel_type = ft.Dropdown(
            value="",
            label="Odor panel type",
            options=[ft.dropdown.Option("1%"), ft.dropdown.Option("10%")],
            # alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=check_complete,
            border_color=ft.colors.SECONDARY_CONTAINER,
            border_width=1,
            focused_border_color=ft.colors.SURFACE_TINT,
            focused_border_width=2,
        )

        self.trial_type = ft.Dropdown(
            value="Multiple",
            label="Type of trials",
            options=[
                ft.dropdown.Option("Single"),
                ft.dropdown.Option("Multiple"),
            ],
            # alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=lambda e: self.trial_type_changed(
                e, update_parent, check_complete
            ),
            border_color=ft.colors.SECONDARY_CONTAINER,
            border_width=1,
            focused_border_color=ft.colors.SURFACE_TINT,
            focused_border_width=2,
        )

        self.single_odor = ft.Dropdown(
            value="1",
            label="Single trial odor",
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            # alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=check_complete,
            border_color=ft.colors.SECONDARY_CONTAINER,
            border_width=1,
            focused_border_color=ft.colors.SURFACE_TINT,
            focused_border_width=2,
        )

        self.num_odors = ft.Dropdown(
            value="",
            label="# of odors",
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            # alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=check_complete,
            border_color=ft.colors.SECONDARY_CONTAINER,
            border_width=1,
            focused_border_color=ft.colors.SURFACE_TINT,
            focused_border_width=2,
        )
        self.num_trials = SettingsFields(
            label="# Trials/odor", on_change=check_complete
        )
        self.odor_duration = SettingsFields(
            label="Odor duration (s)", on_change=check_complete
        )
        self.time_btw_odors = SettingsFields(
            label="Time between odors (s)", on_change=check_complete
        )

    # Arranges setting fields in rows
    def arrange_settings_fields(self, e=None):
        if self.trial_type.value == "Single":
            self.row1 = ft.ResponsiveRow(
                [
                    Column(col={"sm": 3}, controls=[self.panel_type]),
                    Column(col={"sm": 3}, controls=[self.trial_type]),
                    Column(col={"sm": 3}, controls=[self.single_odor]),
                    Column(col={"sm": 3}, controls=[self.odor_duration]),
                ]
            )

            self.row2 = ft.Container()

        if self.trial_type.value == "Multiple":
            self.row1 = ft.ResponsiveRow(
                [
                    Column(col={"sm": 3}, controls=[self.panel_type]),
                    Column(col={"sm": 3}, controls=[self.trial_type]),
                    Column(col={"sm": 3}, controls=[self.num_odors]),
                ]
            )

            self.row2 = ft.ResponsiveRow(
                [
                    Column(col={"sm": 3}, controls=[self.num_trials]),
                    Column(col={"sm": 3}, controls=[self.odor_duration]),
                    Column(col={"sm": 3}, controls=[self.time_btw_odors]),
                ]
            )

    def trial_type_changed(self, e, update_parent, check_complete):
        self.arrange_settings_fields(e)
        self.update()
        update_parent(e)
        check_complete(e)

    def reset_settings_clicked(self, e, keep_paneltype=False):
        self.settings_dict = None
        if keep_paneltype is False:
            self.trial_type.value = "Multiple"
            self.panel_type.value = ""
        self.num_odors.value = ""
        # pdb.set_trace()
        self.num_trials.reset()
        self.odor_duration.reset()
        self.time_btw_odors.reset()

        self.arrange_settings_fields(e)
        self.disable_settings_fields(disable=False)

        self.update()

    def disable_settings_fields(self, disable):
        self.panel_type.disabled = disable
        self.trial_type.disabled = disable
        self.single_odor.disabled = disable
        self.num_odors.disabled = disable
        self.num_trials.disabled = disable
        self.odor_duration.disabled = disable
        self.time_btw_odors.disabled = disable

        self.update()

    def build(self):
        return ft.Column(
            controls=[
                self.row1,
                self.row2,
            ],
        )
