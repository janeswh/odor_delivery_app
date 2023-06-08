import flet as ft
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Container,
    Text,
    icons,
)


class DeliveryApp:
    def __init__(self, page: Page):
        self.page = page
        self.get_directory_dialog = FilePicker(
            on_result=self.get_directory_result
        )
        self.directory_path = Text(col={"sm": 4})
        page.overlay.append(self.get_directory_dialog)

        self.initial_setup()
        self.create_settings_fields()
        row1, row2, row3 = self.arrange_settings_fields()
        self.arrange_view(row1, row2, row3)
        self.page.update()

    def initial_setup(self):
        self.page.title = "Odor Delivery App"

    # Open directory dialog
    def get_directory_result(self, e: FilePickerResultEvent):
        self.directory_path.value = e.path if e.path else "Cancelled!"
        self.directory_path.update()

    # Creates setting input fields
    def create_settings_fields(self):
        self.animal_id = ft.TextField(
            label="Animal ID", hint_text="e.g. 123456-1-2", col={"sm": 4}
        )
        self.roi = ft.TextField(
            label="ROI #",
            col={"sm": 4},
        )

        self.num_odors = ft.Dropdown(
            label="# of odors",
            width=100,
            options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
            alignment=ft.alignment.center,
            col={"sm": 4},
        )

        self.num_trials = ft.TextField(
            label="# Trials/odor",
            col={"sm": 4},
        )
        self.odor_duration = ft.TextField(
            label="Odor duration (s)",
            col={"sm": 4},
        )
        self.time_btw_odors = ft.TextField(
            label="Time between odors (s)", col={"sm": 4}
        )
        self.randomize_option = ft.Switch(
            label="Shuffle trials", value=True, col={"sm": 4}
        )

    # Arranges setting fields in rows
    def arrange_settings_fields(self):
        settings_r1 = ft.ResponsiveRow(
            [
                self.animal_id,
                self.roi,
                self.num_odors,
            ],
        )

        settings_r2 = ft.ResponsiveRow(
            [
                self.odor_duration,
                self.time_btw_odors,
                self.num_trials,
            ]
        )

        # settings_r3 = ft.ResponsiveRow(
        #     [
        #         ElevatedButton(
        #             "Open directory",
        #             icon=icons.FOLDER_OPEN,
        #             col={"sm": 4},
        #             on_click=lambda _: self.get_directory_dialog.get_directory_path(),
        #             disabled=self.page.web,
        #         ),
        #         self.directory_path,
        #         # self.randomize_option,
        #     ]
        # )

        settings_r3 = ft.Row(
            [
                ElevatedButton(
                    "Open directory",
                    icon=icons.FOLDER_OPEN,
                    on_click=lambda _: self.get_directory_dialog.get_directory_path(),
                    disabled=self.page.web,
                ),
                self.directory_path,
                # self.randomize_option,
            ]
        )

        return settings_r1, settings_r2, settings_r3

    def arrange_view(self, row1, row2, row3):
        # self.page.add(
        #     Text("Delivery Settings", style=ft.TextThemeStyle.DISPLAY_MEDIUM)
        # )

        page_title = Text(
            "Delivery Settings", style=ft.TextThemeStyle.DISPLAY_MEDIUM
        )
        directory_prompt = Text(
            "Select experiment folder to save solenoid info"
        )
        directory_button = Container(
            content=ElevatedButton(
                "Open directory",
                icon=icons.FOLDER_OPEN,
                col={"sm": 4},
                on_click=lambda _: self.get_directory_dialog.get_directory_path(),
                disabled=self.page.web,
            ),
        )

        self.view = ft.Column(
            width=600,
            controls=[
                page_title,
                directory_prompt,
                row3,
                # directory_button,
                # self.directory_path,
                row1,
                row2,
            ],
        )

        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        self.page.window_width = 700
        self.page.window_height = 600
        # page.window_resizable = False

        self.page.add(self.view)


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"
        app = DeliveryApp(page)
        # page.add(app) # idk why this doesn't work
        page.update()

    # ft.app(target=main, view=ft.WEB_BROWSER)
    ft.app(target=main)
