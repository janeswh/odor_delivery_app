import flet as ft
from flet import (
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Text,
    icons,
)


def initialize_app(page):
    """
    Sets up App title bar, header messages etc
    """
    page.title = "Odor Delivery App"


def main(page: ft.Page):
    initialize_app(page)

    # page.add(ft.Text(value="Settings"))

    # page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Open directory dialog
    def get_directory_result(e: FilePickerResultEvent):
        directory_path.value = e.path if e.path else "Cancelled!"
        directory_path.update()

    get_directory_dialog = FilePicker(on_result=get_directory_result)
    directory_path = Text(col={"sm": 4})

    page.overlay.append(get_directory_dialog)

    animal_id = ft.TextField(
        label="Animal ID", hint_text="e.g. 123456-1-2", col={"sm": 4}
    )
    roi = ft.TextField(
        label="ROI #",
        col={"sm": 4},
    )

    num_odors = ft.Dropdown(
        label="# of odors",
        width=100,
        options=[ft.dropdown.Option(f"{odor}") for odor in range(1, 9)],
        alignment=ft.alignment.center,
        col={"sm": 4},
    )

    num_trials = ft.TextField(
        label="# Trials/odor",
        col={"sm": 4},
    )
    odor_duration = ft.TextField(
        label="Odor duration (s)",
        col={"sm": 4},
    )
    time_btw_odors = ft.TextField(
        label="Time between odors (s)", col={"sm": 4}
    )
    randomize_option = ft.Switch(
        label="Shuffle trials", value=True, col={"sm": 4}
    )

    settings_r1 = ft.ResponsiveRow(
        [
            animal_id,
            roi,
            num_odors,
        ],
    )

    settings_r2 = ft.ResponsiveRow(
        [
            odor_duration,
            time_btw_odors,
            num_trials,
        ]
    )

    settings_r3 = ft.ResponsiveRow(
        [
            ElevatedButton(
                "Open directory",
                icon=icons.FOLDER_OPEN,
                col={"sm": 4},
                on_click=lambda _: get_directory_dialog.get_directory_path(),
                disabled=page.web,
            ),
            directory_path,
            randomize_option,
        ]
    )

    view = ft.Column(
        width=600, controls=[settings_r1, settings_r2, settings_r3]
    )

    # view = ft.Column(
    #     width=600,
    #     controls=[
    #         animal_id,
    #         roi,
    #         num_odors,
    #         num_trials,
    #         odor_duration,
    #         time_btw_odors,
    #         randomize_option,
    #     ],
    # )

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window_width = 700
    page.window_height = 600
    # page.window_resizable = False

    page.add(view)

    # page.add(
    #     animal_id,
    #     roi,
    #     num_odors,
    #     num_trials,
    #     odor_duration,
    #     time_btw_odors,
    #     randomize_option,
    # )


ft.app(target=main)
