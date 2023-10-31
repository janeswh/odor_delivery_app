"""Main script that calls and runs the Flet app.

Per https://flet.dev/docs/guides/python/getting-started, a Page is the base
app canvas, and elements are added and removed from the page to build the
app UI. In this script, the OdorDeliveryApp control is added to the empty Page
that we instantiate in this script.
"""

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
