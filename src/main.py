import flet as ft
from flet import Page
from components.app_layout import OdorDeliveryApp


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"
        page.theme_mode = ft.ThemeMode.DARK
        app = OdorDeliveryApp(page)

        page.add(app)
        page.update()

    ft.app(target=main)
