from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivymd.uix.widget import Widget


from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
import pdb


class SettingsScreen(Widget):
    animal_id = ObjectProperty(None)
    roi = ObjectProperty(None)
    num_odors = ObjectProperty(None)
    num_trials = ObjectProperty(None)
    odor_duration = ObjectProperty(None)
    odor_interval = ObjectProperty(None)


class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = Builder.load_file("design.kv")
        odor_menu_items = [
            {
                "viewclass": "OneLineListItem",
                "height": dp(56),
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_odor_item(x),
            }
            for i in range(1, 9)
        ]

        trials_menu_items = [
            {
                "viewclass": "OneLineListItem",
                "height": dp(56),
                "text": f"{i}",
                "on_release": lambda x=f"{i}": self.set_trial_item(x),
            }
            for i in range(1, 6)
        ]

        self.odors_menu = MDDropdownMenu(
            caller=self.main_layout.ids.num_odors_field,
            items=odor_menu_items,
            position="bottom",
            width_mult=4,
            max_height=dp(224),
        )

        self.trials_menu = MDDropdownMenu(
            caller=self.main_layout.ids.num_trials_field,
            items=trials_menu_items,
            position="bottom",
            width_mult=4,
            max_height=dp(224),
        )

    def set_odor_item(self, text__item):
        self.main_layout.ids.num_odors_field.text = text__item
        self.odors_menu.dismiss()

    def set_trial_item(self, text__item):
        self.main_layout.ids.num_trials_field.text = text__item
        self.odors_menu.dismiss()

    def build(self):
        # self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        return self.main_layout
        # return SettingsScreen()


MainApp().run()
