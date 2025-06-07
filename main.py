# main.py

from kivy.resources import resource_find
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import hashlib

from app.data_manager import (
    fetch_all_sites,
    register_user,
    get_user_by_email,
    update_password
)

# Load all KV files
Builder.load_file('ui/home.kv')
Builder.load_file('ui/signup.kv')
Builder.load_file('ui/forgot.kv')
Builder.load_file('ui/map.kv')
Builder.load_file('ui/details.kv')
Builder.load_file('ui/admin.kv')


class HomeScreen(Screen):
    def on_pre_enter(self):
        self.sites = fetch_all_sites()
        self.update_translations()  # refresh text + font
        print("Loaded sites:", self.sites)

    def update_translations(self):
        app = App.get_running_app()
        lang = app.i18n['locale']

        # ── 0) resolve all font paths ─────────────────────────────────────
        hi_font = resource_find('data/fonts/NotoSansDevanagari-Regular.ttf')
        kn_font = resource_find('data/fonts/NotoSansKannada-Regular.ttf')
        en_font = resource_find('data/fonts/Roboto-Regular.ttf')

        # pick your “label” font by locale
        label_font = {'hi': hi_font, 'kn': kn_font}.get(lang, en_font)

        # ── 1) labels & buttons ───────────────────────────────────────
        for wid_id, key in (
                ('title_label', 'Divine Maps'),
                ('tagline_label', 'Spiritual Exploration Made Simple'),
                ('login_button', 'Login'),
        ):
            w = self.ids[wid_id]
            w.text = app.get_translations(key)
            w.font_name = label_font

        # ── 2) the three “links” ──────────────────────────────────────
        for wid_id, key in (
                ('signup_label', 'Sign Up'),
                ('forgot_label', 'Forgot Password'),
                ('guest_label', 'Continue as Guest'),
        ):
            w = self.ids[wid_id]
            w.text = f"[ref={wid_id}]{app.get_translations(key)}[/ref]"
            w.font_name = label_font

        # ── 3) quote, version, terms/privacy ─────────────────────────
        self.ids.quote_label.text = app.get_translations('Quote')
        self.ids.version_label.text = app.get_translations('Version v1.0.0')
        self.ids.terms_label.text = (
            f"[ref=terms]{app.get_translations('Terms')}[/ref] | "
            f"[ref=privacy]{app.get_translations('Privacy')}[/ref]"
        )
        for wid in ('quote_label', 'version_label', 'terms_label'):
            self.ids[wid].font_name = label_font

        # ── 4) TextInputs: set appropriate font depending on language ─────────────
        if lang == 'hi':
            input_font = hi_font
        elif lang == 'kn':
            input_font = kn_font
        else:
            input_font = en_font

        self.ids.username_input.hint_text = app.get_translations('Enter username')
        self.ids.password_input.hint_text = app.get_translations('Enter password')
        self.ids.username_input.font_name = input_font
        self.ids.password_input.font_name = input_font

    def do_login(self, username, password):
        print(f"Logging in with {username}:{password}")
        # TODO: Validate + navigate

    def go_to_signup(self):
        self.manager.current = 'signup'

    def go_to_forgot(self):
        self.manager.current = 'forgot'

    def continue_as_guest(self):
        print("Continuing as guest")

    def open_terms(self):
        print("Opening terms and conditions")

    def open_privacy(self):
        print("Opening privacy policy")


class SignUpScreen(Screen):
    def go_back(self):
        self.manager.current = 'home'

    def on_signup_button(self):
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text
        confirm_password = self.ids.confirm_password_input.text

        if not (username and email and password and confirm_password):
            print("[Error] All fields are required.")
            return

        if password != confirm_password:
            print("[Error] Password and Confirm Password do not match.")
            return

        if len(password) < 6:
            print("[Error] Password must be at least 6 characters.")
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        result = register_user(username, email, pw_hash)
        if result.get("success"):
            new_id = result["user_id"]
            print(f"[Success] Registered new user with ID: {new_id}")
            self.manager.current = 'home'
        else:
            print(f"[Error] Could not register: {result.get('error')}")


class ForgotPasswordScreen(Screen):
    def go_back(self):
        self.manager.current = 'home'

    def on_reset_button(self):
        email = self.ids.email_input.text.strip()
        new_password = self.ids.new_password_input.text
        confirm_new_password = self.ids.confirm_new_password_input.text

        if not (email and new_password and confirm_new_password):
            print("[Error] All fields are required.")
            return

        if new_password != confirm_new_password:
            print("[Error] Passwords do not match.")
            return

        if len(new_password) < 6:
            print("[Error] Password must be at least 6 characters.")
            return

        user = get_user_by_email(email)
        if not user:
            print("[Error] Email not found.")
            return

        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        result = update_password(email, new_hash)
        if result.get("success"):
            print("[Success] Password updated successfully.")
            self.manager.current = 'home'
        else:
            print(f"[Error] Could not update password: {result.get('error')}")


class DivineMapsApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.i18n = {'locale': 'en'}
        self.translations = self.load_translations()

    def load_translations(self):
        return {
            'en': {
                'Divine Maps': 'Divine Maps',
                'Spiritual Exploration Made Simple': 'Spiritual Exploration Made Simple',
                'Login': 'Login',
                'Sign Up': 'Sign Up',
                'Continue as Guest': 'Continue as Guest',
                'Forgot Password': 'Forgot Password',
                'Terms': 'Terms',
                'Privacy': 'Privacy',
                'Version v1.0.0': 'Version v1.0.0',
                'Quote': '"Faith is seeing light with your heart when all your eyes see is darkness"',
                'Enter username': 'Enter username',
                'Enter password': 'Enter password'
            },
            'hi': {
                'Divine Maps': 'दिव्य मानचित्र',
                'Spiritual Exploration Made Simple': 'आध्यात्मिक अन्वेषण सरल बनाया',
                'Login': 'लॉग इन करें',
                'Sign Up': 'साइन अप करें',
                'Continue as Guest': 'अतिथि के रूप में जारी रखें',
                'Forgot Password': 'पासवर्ड भूल गए',
                'Terms': 'नियम और शर्तें',
                'Privacy': 'गोपनीयता',
                'Version v1.0.0': 'संस्करण v1.0.0',
                'Quote': '"विश्वास वह है जब आपके हृदय से प्रकाश आता है, भले ही आँखें अंधकार देखें"',
                'Enter username': 'उपयोगकर्ता नाम दर्ज करें',
                'Enter password': 'पासवर्ड दर्ज करें'
            },
            'kn': {
                'Divine Maps': 'ದಿವ್ಯ ನಕ್ಷೆಗಳು',
                'Spiritual Exploration Made Simple': 'ಆಧ್ಯಾತ್ಮಿಕ ಅನ್ವೇಷಣೆಯನ್ನು ಸರಳಗೊಳಿಸಲಾಗಿದೆ',
                'Login': 'ಲಾಗಿನ್',
                'Sign Up': 'ಸೈನ್ ಅಪ್',
                'Continue as Guest': 'ಅತಿಥಿಯಾಗಿ ಮುಂದುವರಿಸಿ',
                'Forgot Password': 'ಪಾಸ್ವರ್ಡ್ ಮರೆತಿರಾ',
                'Terms': 'ನಿಯಮಗಳು',
                'Privacy': 'ಗೌಪ್ಯತೆ',
                'Version v1.0.0': 'ಆವೃತ್ತಿ v1.0.0',
                'Quote': '"ನಂಬಿಕೆ ಎಂದರೆ ನಿಮ್ಮ ಹೃದಯದಿಂದ ಬೆಳಕನ್ನು ನೋಡುವುದು, ನಿಮ್ಮ ಕಣ್ಣುಗಳು ಕೇವಲ ಕತ್ತಲೆಯನ್ನು ನೋಡಿದಾಗ"',
                'Enter username': 'ಬಳಕೆದಾರ ಹೆಸರನ್ನು ನಮೂದಿಸಿ',
                'Enter password': 'ಗುಪ್ತಪದವನ್ನು ನಮೂದಿಸಿ'
            }
        }

    def get_translations(self, key):
        current_lang = self.i18n['locale']
        return self.translations.get(current_lang, {}).get(
            key, self.translations.get('en', {}).get(key, key)
        )

    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(ForgotPasswordScreen(name='forgot'))
        return sm


if __name__ == '__main__':
    DivineMapsApp().run()
