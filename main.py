# main.py
import mysql.connector
import i18n
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from app.data_manager import fetch_all_sites

# 1) Load translations
i18n.load_path.append('i18n')
i18n.set('locale', 'en')  # or 'kn', 'hi', etc.

# 2) Define your screens
class HomeScreen(Screen):
    def on_pre_enter(self):
        # Fetch all sites when this screen is about to show
        sites = fetch_all_sites()
        print("Loaded sites:", sites)
        # You could also store `sites` on `self` for binding into your UI
        self.sites = sites

# 3) Set up ScreenManager
class DivineMapsApp(App):
    def build(self):
        # Load your Kivy layouts
        Builder.load_file('ui/home.kv')
        Builder.load_file('ui/map.kv')
        Builder.load_file('ui/details.kv')
        Builder.load_file('ui/admin.kv')

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        # TODO: add other screens, e.g. MapScreen(name='map'), DetailsScreen(name='details'), AdminScreen(name='admin')
        return sm

    def get_translation(self, key):
        """Helper to retrieve translated strings in KV via app.get_translation()."""
        return i18n.t(key)

if __name__ == "__main__":
    DivineMapsApp().run()
