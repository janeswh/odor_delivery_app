from kivymd.app import MDApp

# from kivymd.uix.label import MDLabel

# from kivymd.uix.gridlayout import MDGridLayout
# # from kivymd.uix.floatlayout import MDFloatLayout
# from kivymd.uix.anchorlayout import MDAnchorLayout


# from kivymd.uix.textfield import MDTextField
# from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.widget import Widget
from kivy.properties import ObjectProperty


class SettingsScreen(Widget):
    animal_id = ObjectProperty(None)
    roi = ObjectProperty(None)
    num_odors = ObjectProperty(None)
    num_trials = ObjectProperty(None)

    # def spinner_clicked(self, value):
    #     self.ids.click_label.text = f'# of Odors: {value}'


class MainApp(MDApp):
    def build(self):
        # return MDLabel(text="Hello, World", halign="center")
        return SettingsScreen()


MainApp().run()
