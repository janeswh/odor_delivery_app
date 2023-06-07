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
from kivymd.uix.screen import MDScreen


class SettingsScreen(Widget):
    animal_id = ObjectProperty(None)
    roi = ObjectProperty(None)
    num_odors = ObjectProperty(None)
    num_trials = ObjectProperty(None)


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        num_odors_list = list(range(1, 9))
        self.menu = MDDropdownMenu(
            caller=MDScreen.ids.field,
            items=num_odors_list,
            position="bottom",
        )

    def build(self):
        # return MDLabel(text="Hello, World", halign="center")
        return SettingsScreen()


MainApp().run()
