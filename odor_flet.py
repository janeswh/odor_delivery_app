import flet as ft


def main(page: ft.Page):
    page.title = "Odor Delivery App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    animal_id = ft.TextField(label="Animal ID")
    page.add(animal_id)


ft.app(target=main)
