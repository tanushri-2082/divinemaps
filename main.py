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
Builder.load_file('ui/terms.kv')
Builder.load_file('ui/privacy.kv')
Builder.load_file('ui/map.kv')
Builder.load_file('ui/details.kv')
Builder.load_file('ui/admin.kv')


class HomeScreen(Screen):
    def on_pre_enter(self):
        self.sites = fetch_all_sites()
        self.update_translations()  # refresh text + font
        print("Loaded sites:", self.sites)

    def update_translations(self):
        """
        Called whenever the locale changes (or when HomeScreen appears).
        Re‐sets each widget’s .text AND, if needed, .font_name based on app.i18n['locale'].
        """
        app = App.get_running_app()
        lang = app.i18n['locale']
        self.ids.lang_selector.text = app.i18n['locale']
        # Decide which font to use; None means “use default Kivy font” (no override)
        if lang == 'hi':
            chosen_font = 'data/fonts/NotoSansDevanagari-Regular.ttf'
        elif lang == 'kn':
            chosen_font = 'data/fonts/NotoSansKannada-Regular.ttf'
        else:
            chosen_font = resource_find('data/fonts/Roboto-Regular.ttf')

        # ─── Update each translatable widget’s text ─────────────────────────────────
        def apply_font(widget):
            widget.font_name = chosen_font
        # Title
        self.ids.title_label.text = app.get_translations('Divine Maps')
        if chosen_font:
            self.ids.title_label.font_name = chosen_font

        # Tagline
        self.ids.tagline_label.text = app.get_translations('Spiritual Exploration Made Simple')
        if chosen_font:
            self.ids.tagline_label.font_name = chosen_font

        # Username input (hint text)
        self.ids.username_input.hint_text = app.get_translations('Enter username')
        if chosen_font:
            self.ids.username_input.font_name = chosen_font

        # Password input (hint text)
        self.ids.password_input.hint_text = app.get_translations('Enter password')
        if chosen_font:
            self.ids.password_input.font_name = chosen_font

        # Login button
        self.ids.login_button.text = app.get_translations('Login')
        if chosen_font:
            self.ids.login_button.font_name = chosen_font

        # Sign Up link
        self.ids.signup_label.text = "[ref=signup]" + app.get_translations('Sign Up') + "[/ref]"
        if chosen_font:
            self.ids.signup_label.font_name = chosen_font

        # Forgot Password link
        self.ids.forgot_label.text = "[ref=forgot]" + app.get_translations('Forgot Password') + "[/ref]"
        if chosen_font:
            self.ids.forgot_label.font_name = chosen_font

        # Continue as Guest link
        self.ids.guest_label.text = "[ref=guest]" + app.get_translations('Continue as Guest') + "[/ref]"
        if chosen_font:
            self.ids.guest_label.font_name = chosen_font

        # Spiritual Quote
        self.ids.quote_label.text = app.get_translations('Quote')
        if chosen_font:
            self.ids.quote_label.font_name = chosen_font

        # Footer: Version
        self.ids.version_label.text = app.get_translations('Version v1.0.0')
        if chosen_font:
            self.ids.version_label.font_name = chosen_font

        # Footer: Terms | Privacy
        self.ids.terms_label.text = (
            "[ref=terms]" + app.get_translations('Terms') + "[/ref] | "
            "[ref=privacy]" + app.get_translations('Privacy') + "[/ref]"
        )
        if chosen_font:
            self.ids.terms_label.font_name = chosen_font

        # Finally, update the Spinner’s displayed text so it still shows the selected locale.
        self.ids.lang_selector.text = app.i18n['locale']
        if lang == 'hi':
            self.ids.lang_selector.font_name = 'data/fonts/NotoSansDevanagari-Regular.ttf'
        elif lang == 'kn':
            self.ids.lang_selector.font_name = 'data/fonts/NotoSansKannada-Regular.ttf'
        else:
            # Reset to default or English-compatible font
            self.ids.lang_selector.font_name = 'data/fonts/Roboto-Regular.ttf'  # use your actual English font path

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
        self.manager.current = 'terms'
        print("Opening terms and conditions")

    def open_privacy(self):
        self.manager.current = 'privacy'
        print("Opening privacy policy")

class TermsScreen(Screen):
    def go_back(self):
        self.manager.current = 'home'

class PrivacyScreen(Screen):
    def go_back(self):
        self.manager.current = 'home'


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
                'Enter password': 'Enter password',
                'Terms and Conditions': 'Terms and Conditions',
                'Privacy Policy': 'Privacy Policy',
                'Back': 'Back',
                'terms_content': """
        1. Acceptance of Terms:
        By using Divine Maps, you agree to be bound by these Terms and Conditions...

        2. User Accounts:
        You are responsible for maintaining the confidentiality of your account...

        [More detailed terms content here...]""",
                'privacy_content': """
        1. Information We Collect
        We collect personal information when you register...

        2. How We Use Information
        We use your information to provide and improve our services...

        [More detailed privacy content here...]"""
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
                'Enter password': 'पासवर्ड दर्ज करें',
                'Terms and Conditions': 'नियम और शर्तें',
                'Privacy Policy': 'गोपनीयता नीति',
                'Back': 'वापस',
                'terms_content': """
        1. नियमों की स्वीकृति
        दिव्य मानचित्र का उपयोग करके, आप इन नियमों और शर्तों से बंधे होने के लिए सहमत होते हैं...

        [More Hindi content here...]""",
                'privacy_content': """
        1. हम कौन सी जानकारी एकत्र करते हैं
        जब आप पंजीकरण करते हैं तो हम व्यक्तिगत जानकारी एकत्र करते हैं...

        [More Hindi content here...]"""
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
                'Enter password': 'ಗುಪ್ತಪದವನ್ನು ನಮೂದಿಸಿ',
                'Terms and Conditions': 'ನಿಯಮಗಳು ಮತ್ತು ಷರತ್ತುಗಳು',
                'Privacy Policy': 'ಗೌಪ್ಯತಾ ನೀತಿ',
                'Back': 'ಹಿಂದಕ್ಕೆ',
                'terms_content': """
        1. ನಿಯಮಗಳ ಸ್ವೀಕಾರ
        ದಿವ್ಯ ನಕ್ಷೆಗಳನ್ನು ಬಳಸುವ ಮೂಲಕ, ನೀವು ಈ ನಿಯಮಗಳು ಮತ್ತು ಷರತ್ತುಗಳಿಗೆ ಬದ್ಧರಾಗಿರುತ್ತೀರಿ...

        [More Kannada content here...]""",
                'privacy_content': """
        1. ನಾವು ಸಂಗ್ರಹಿಸುವ ಮಾಹಿತಿ
        ನೀವು ನೋಂದಾಯಿಸಿದಾಗ ನಾವು ವೈಯಕ್ತಿಕ ಮಾಹಿತಿಯನ್ನು ಸಂಗ್ರಹಿಸುತ್ತೇವೆ...

        [More Kannada content here...]"""
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
        sm.add_widget(TermsScreen(name='terms'))  # Add this
        sm.add_widget(PrivacyScreen(name='privacy'))
        return sm


if __name__ == '__main__':
    DivineMapsApp().run()
