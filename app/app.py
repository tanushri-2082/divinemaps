import os
import yaml
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen

# Import all your screens in one go
from .screens import (
    LoginScreen, SignUpScreen, DetailsScreen, TermsScreen,
    PrivacyScreen, ForgotPasswordScreen, GuestScreen,
    HomeScreen, SettingsScreen, ReligionScreen, HelpScreen,
    MapsScreen, SiteDetailScreen, SiteListScreen, TempleSelectionScreen
)

class DivineMapsApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.locale = 'en'
        self.translations = {}
        self.current_user_id = None
        self.load_translations()

    def email_filter(self, substring, from_undo):
        """
        Called by Kivy TextInput.input_filter.
        Keeps only letters, digits, @ . - _ in the incoming text.
        """
        allowed = set("abcdefghijklmnopqrstuvwxyz"
                      "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      "0123456789@.-_")
        return "".join(ch for ch in substring if ch in allowed)


    def load_translations(self):
        base = os.path.join(os.path.dirname(__file__), '..', 'translations')
        for loc in ('en', 'hi', 'kn'):
            path = os.path.join(base, f"{loc}.yml")
            try:
                with open(path, encoding='utf-8') as f:
                    self.translations[loc] = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading translations for {loc}: {e}")
                self.translations[loc] = {}

    def get_translations(self, key):
        data = self.translations.get(self.locale, {})
        return data.get(key, self.translations['en'].get(key, key))

    def set_locale(self, locale_code):
        self.locale = locale_code if locale_code in self.translations else 'en'
        # Re‐run on_pre_enter on each screen that has it
        if hasattr(self, 'root') and self.root:
            for screen in self.root.screens:
                if hasattr(screen, 'on_pre_enter'):
                    try:
                        screen.on_pre_enter()
                    except Exception:
                        pass

    def build(self):
        # Find your UI folder (one level up from this file)
        here   = os.path.dirname(__file__)
        base   = os.path.dirname(here)
        kv_dir = os.path.join(base, 'ui')

        # Load all your .kv files, including help.kv
        for name in (
                'login', 'signup', 'details', 'terms', 'privacy',
                'forgot', 'home', 'guest', 'settings', 'religion', 'help',
                'maps', 'site_detail', 'site_list', 'temple_selection'
        ):
            Builder.load_file(os.path.join(kv_dir, f"{name}.kv"))

        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(DetailsScreen(name='details'))
        sm.add_widget(TermsScreen(name='terms'))
        sm.add_widget(PrivacyScreen(name='privacy'))
        sm.add_widget(ForgotPasswordScreen(name='forgot'))
        sm.add_widget(GuestScreen(name='guest'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(ReligionScreen(name='religion'))
        sm.add_widget(HelpScreen(name='help'))
        sm.add_widget(MapsScreen(name='maps'))
        sm.add_widget(SiteDetailScreen(name='site_detail'))
        sm.add_widget(SiteListScreen(name='site_list'))
        sm.add_widget(TempleSelectionScreen(name='temple_selection'))
        return sm