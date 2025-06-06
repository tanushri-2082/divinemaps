# main.py

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from app.data_manager import fetch_all_sites

# Load KV files only once
Builder.load_file('ui/home.kv')
Builder.load_file('ui/map.kv')
Builder.load_file('ui/details.kv')
Builder.load_file('ui/admin.kv')

# Screen definitions
class HomeScreen(Screen):
    def on_pre_enter(self):
        self.sites = fetch_all_sites()
        print("Loaded sites:", self.sites)

    def do_login(self, username, password):
        print(f"Logging in with {username}:{password}")
        # TODO: Validate with database and navigate

    def go_to_signup(self):
        print("Navigating to signup screen")

    def go_to_forgot(self):
        print("Navigating to forgot password screen")

    def continue_as_guest(self):
        print("Continuing as guest")
        # TODO: Navigate as guest

    def open_terms(self):
        print("Opening terms and conditions")

    def open_privacy(self):
        print("Opening privacy policy")

# Main App
class DivineMapsApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.i18n = {'locale': 'en'}  # Default language
        self.translations = self.load_translations()

    def load_translations(self):
        """Load translations from a hard-coded dictionary."""
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
        """Get a translated string for the current language (fallback to English)."""
        current_lang = self.i18n['locale']
        return self.translations.get(current_lang, {}).get(
            key,
            self.translations.get('en', {}).get(key, key)
        )

    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

if __name__ == '__main__':
    DivineMapsApp().run()
