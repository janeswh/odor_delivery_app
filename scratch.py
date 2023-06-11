import flet as ft
from flet import (
    UserControl,
    TextField,
    Ref,
    Column,
    ElevatedButton,
    FilePicker,
    FilePickerResultEvent,
    Page,
    Row,
    Container,
    Text,
    icons,
)

from simpledt import DataFrame
import pandas as pd
import datetime
import random
import serial
import os
import pdb


class TrialsTable(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        # self.display_content = Container(Row(controls=[Text("default")]))
        self.display_content = Container(
            content=Row(
                controls=[
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("First name")),
                            ft.DataColumn(ft.Text("Last name")),
                            ft.DataColumn(ft.Text("Age"), numeric=True),
                        ],
                        rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("John")),
                                    ft.DataCell(ft.Text("Smith")),
                                    ft.DataCell(ft.Text("43")),
                                ],
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Jack")),
                                    ft.DataCell(ft.Text("Brown")),
                                    ft.DataCell(ft.Text("19")),
                                ],
                            ),
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(ft.Text("Alice")),
                                    ft.DataCell(ft.Text("Wong")),
                                    ft.DataCell(ft.Text("25")),
                                ],
                            ),
                        ],
                    ),
                ]
            )
        )

    def change(self):
        # self.display_content.content = Row(controls=[Text("changed")])
        self.display_content.content = Row(
            controls=[
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("CITY")),
                        ft.DataColumn(ft.Text("FUN")),
                        ft.DataColumn(ft.Text("DOGS")),
                    ],
                    rows=[
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text("DOGS")),
                                ft.DataCell(ft.Text("DOGS")),
                                ft.DataCell(ft.Text("DOGS")),
                            ],
                        ),
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text("DOGS")),
                                ft.DataCell(ft.Text("DOGS")),
                                ft.DataCell(ft.Text("DOGS")),
                            ],
                        ),
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text("DOGS")),
                                ft.DataCell(ft.Text("DOGS")),
                                ft.DataCell(ft.Text("DOGS")),
                            ],
                        ),
                    ],
                ),
            ]
        )

        # self.display_content = Container(
        #     content=ft.DataTable(
        #         columns=[
        #             ft.DataColumn(ft.Text("CITY")),
        #             ft.DataColumn(ft.Text("FUN")),
        #             ft.DataColumn(ft.Text("DOGS")),
        #         ],
        #         rows=[
        #             ft.DataRow(
        #                 cells=[
        #                     ft.DataCell(ft.Text("DOGS")),
        #                     ft.DataCell(ft.Text("DOGS")),
        #                     ft.DataCell(ft.Text("DOGS")),
        #                 ],
        #             ),
        #             ft.DataRow(
        #                 cells=[
        #                     ft.DataCell(ft.Text("DOGS")),
        #                     ft.DataCell(ft.Text("DOGS")),
        #                     ft.DataCell(ft.Text("DOGS")),
        #                 ],
        #             ),
        #             ft.DataRow(
        #                 cells=[
        #                     ft.DataCell(ft.Text("DOGS")),
        #                     ft.DataCell(ft.Text("DOGS")),
        #                     ft.DataCell(ft.Text("DOGS")),
        #                 ],
        #             ),
        #         ],
        #     ),
        # )

        self.update()

    def build(self):
        return self.display_content


class MiddleLayout(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.exp_display_content = Text("Middle Layout init")
        self.table = TrialsTable(self.page)

    def make_change_button(self):
        self.randomize_button = ElevatedButton(
            "Change", on_click=self.change_table
        )

    def change_table(self, e):
        self.table.change()

    def build(self):
        self.make_change_button()
        return Column(controls=[self.randomize_button, self.table])


class OdorDeliveryApp(UserControl):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.page.title = "Odor Delivery App"

        self.main_content = MiddleLayout(self.page)

        self.page.update()

    def build(self):
        return self.main_content


if __name__ == "__main__":

    def main(page: Page):
        page.title = "Odor Delivery App"
        app = OdorDeliveryApp(page)

        page.add(app)
        page.update()

    ft.app(target=main)
