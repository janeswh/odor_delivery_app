import flet as ft
from flet import (
    UserControl,
    TextField,
    Column,
    Page,
)


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


class SettingsLayout(UserControl):
    def __init__(
        self,
        page: Page,
        directory_path,
        check_complete,
    ):
        super().__init__()

        self.page = page
        self.directory_path = directory_path
        self.settings_dict = None
        self.saved_click = False

        self.animal_id = SettingsFields(
            # ref=self.textfield1_ref,
            label="Animal ID",
            on_change=check_complete,
        )

        self.roi = SettingsFields(label="ROI", on_change=check_complete)

        self.num_odors = ft.Dropdown(
            value="",
            label="# of odors",
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            # alignment=ft.alignment.center,
            col={"sm": 4},
            on_change=check_complete,
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

        # self.create_settings_fields()
        self.arrange_settings_fields()

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

    # Arranges setting fields in rows
    def arrange_settings_fields(self):
        self.row1 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.animal_id]),
                Column(col={"sm": 4}, controls=[self.roi]),
                Column(col={"sm": 4}, controls=[self.num_odors]),
            ]
        )

        self.row2 = ft.ResponsiveRow(
            [
                Column(col={"sm": 4}, controls=[self.odor_duration]),
                Column(col={"sm": 4}, controls=[self.time_btw_odors]),
                Column(col={"sm": 4}, controls=[self.num_trials]),
            ]
        )

    def reset_settings_clicked(self, e):
        self.settings_dict = None
        self.animal_id.reset()
        self.roi.reset()
        self.num_odors.value = ""
        self.num_trials.reset()
        self.odor_duration.reset()
        self.time_btw_odors.reset()

        self.disable_settings_fields(disable=False)

        self.update()

    def disable_settings_fields(self, disable):
        self.animal_id.disabled = disable
        self.roi.disabled = disable
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
