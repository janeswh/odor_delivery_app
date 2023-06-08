from kivymd.app import MDApp
from kivy.lang import Builder


# from kivymd.uix.label import MDLabel

# from kivymd.uix.gridlayout import MDGridLayout
# # from kivymd.uix.floatlayout import MDFloatLayout
# from kivymd.uix.anchorlayout import MDAnchorLayout


# from kivymd.uix.textfield import MDTextField
# from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.widget import Widget
from kivy.properties import ObjectProperty

from kivymd.uix.menu import MDDropdownMenu


class SettingsScreen(Widget):
    animal_id = ObjectProperty(None)
    roi = ObjectProperty(None)
    num_odors = ObjectProperty(None)
    num_trials = ObjectProperty(None)

    # def spinner_clicked(self, value):
    #     self.ids.click_label.text = f'# of Odors: {value}'


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen = Builder.load_file("design.kv")

        menu_items = [
            {
                "text": f"Item {i}",
                "on_release": lambda x=f"Item {i}": self.set_item(x),
            }
            for i in range(5)
        ]

        self.menu = MDDropdownMenu(
            caller=self.screen.ids.field,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )

    def set_item(self, text_item):
        self.screen.ids.field.text = text_item
        self.menu.dismiss()

    def build(self):
        # return MDLabel(text="Hello, World", halign="center")
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return SettingsScreen()


MainApp().run()
