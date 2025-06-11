# main.py

import os
import hashlib
import yaml
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.resources import resource_find

from kivymd.app import MDApp
from kivymd.uix.pickers.datepicker import MDDatePicker
from kivymd.uix.button import MDIconButton  # for calendar icon
from kivymd.uix.button import MDRaisedButton  # for “Continue” button styling


from app.data_manager import (
    fetch_all_sites,
    register_user,
    get_user_by_email,
    update_password,
    update_user_details,
    validate_user_credentials
)

# Load KV files
Builder.load_file('ui/login.kv')
Builder.load_file('ui/signup.kv')
Builder.load_file('ui/details.kv')
Builder.load_file('ui/terms.kv')
Builder.load_file('ui/privacy.kv')
Builder.load_file('ui/forgot.kv')
Builder.load_file('ui/map.kv')
Builder.load_file('ui/guest.kv')
Builder.load_file('ui/admin.kv')


class LoginScreen(Screen):
    def on_pre_enter(self):
        self.update_translations()

    def update_translations(self):
        app = App.get_running_app()
        # Retrieve current locale (fallback to 'en')
        try:
            lang = app.locale
        except Exception:
            lang = 'en'
        # Fonts
        hi_font = resource_find('data/fonts/NotoSansDevanagari-Regular.ttf')
        kn_font = resource_find('data/fonts/NotoSansKannada-Regular.ttf')
        en_font = resource_find('data/fonts/Roboto-Regular.ttf')
        label_font = {'hi': hi_font, 'kn': kn_font}.get(lang, en_font)
        input_font = {'hi': hi_font, 'kn': kn_font}.get(lang, en_font)

        # Title label
        if 'title_label' in self.ids:
            self.ids.title_label.text = app.get_translations('Divine Maps')
            self.ids.title_label.font_name = label_font
        if 'tagline_label' in self.ids:
            self.ids.tagline_label.text = app.get_translations('Spiritual Exploration Made Simple')
            self.ids.tagline_label.font_name = label_font

        # Username/password hints
        if 'username_input' in self.ids:
            self.ids.username_input.hint_text = app.get_translations('Enter username')
            self.ids.username_input.font_name = input_font
        if 'password_input' in self.ids:
            self.ids.password_input.hint_text = app.get_translations('Enter password')
            self.ids.password_input.font_name = input_font

        # Login button
        if 'login_button' in self.ids:
            self.ids.login_button.text = app.get_translations('Login')
            self.ids.login_button.font_name = label_font

        # Links: Sign Up / Forgot / Guest
        if 'signup_label' in self.ids:
            self.ids.signup_label.text = f"[ref=signup]{app.get_translations('Sign Up')}[/ref]"
            self.ids.signup_label.font_name = label_font
        if 'forgot_label' in self.ids:
            self.ids.forgot_label.text = f"[ref=forgot]{app.get_translations('Forgot Password')}[/ref]"
            self.ids.forgot_label.font_name = label_font
        if 'guest_label' in self.ids:
            self.ids.guest_label.text = f"[ref=guest]{app.get_translations('Continue as Guest')}[/ref]"
            self.ids.guest_label.font_name = label_font

        # Quote
        if 'quote_label' in self.ids:
            self.ids.quote_label.text = app.get_translations('Quote')
            self.ids.quote_label.font_name = label_font

        # Version & terms
        if 'version_label' in self.ids:
            self.ids.version_label.text = app.get_translations('Version v1.0.0')
            self.ids.version_label.font_name = label_font
        if 'terms_label' in self.ids:
            self.ids.terms_label.text = f"[ref=terms]{app.get_translations('Terms')}[/ref] | [ref=privacy]{app.get_translations('Privacy')}[/ref]"
            self.ids.terms_label.font_name = label_font

    def do_login(self, username, password):
        app = App.get_running_app()
        # Validate credentials
        if not username or not password:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('All fields required')),
                size_hint=(0.6, 0.4)
            ).open()
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        user = validate_user_credentials(username, pw_hash)
        if user:
            # Login successful; store current_user_id
            app.current_user_id = user['user_id']
            # Navigate onward, e.g. main map
            self.manager.current = 'map'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Invalid credentials')),
                size_hint=(0.6, 0.4)
            ).open()

    def go_to_signup(self):
        self.manager.current = 'signup'

    def go_to_forgot(self):
        # Reverted: go to single forgot screen
        self.manager.current = 'forgot'

    def continue_as_guest(self):
        self.manager.current = 'guest'

    def open_terms(self):
        self.manager.current = 'terms'

    def open_privacy(self):
        self.manager.current = 'privacy'


class TermsScreen(Screen):
    def go_back(self):
        self.manager.current = 'login'

class PrivacyScreen(Screen):
    def go_back(self):
        self.manager.current = 'login'


class SignUpScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        # Translations for signup screen
        if 'signup_title' in self.ids:
            self.ids.signup_title.text = app.get_translations('Sign Up')
        if 'username_input' in self.ids:
            self.ids.username_input.hint_text = app.get_translations('Enter username')
        if 'email_input' in self.ids:
            self.ids.email_input.hint_text = app.get_translations('Enter email')
        if 'password_input' in self.ids:
            self.ids.password_input.hint_text = app.get_translations('Enter password')
        if 'confirm_password_input' in self.ids:
            self.ids.confirm_password_input.hint_text = app.get_translations('Re-enter password')
        if 'signup_button' in self.ids:
            self.ids.signup_button.text = app.get_translations('Sign Up')

    def go_back(self):
        self.manager.current = 'login'

    def on_signup_button(self):
        app = App.get_running_app()
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text
        confirm = self.ids.confirm_password_input.text

        if not (username and email and password and confirm):
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('All fields required')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        if password != confirm:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Passwords do not match')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        if len(password) < 6:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Password must be at least 6 characters.')),
                size_hint=(0.6, 0.4)
            ).open()
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        res = register_user(username, email, pw_hash)
        if res.get('success'):
            app.current_user_id = res['user_id']
            # Navigate to details screen
            self.manager.current = 'details'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=res.get('error', '')),
                size_hint=(0.6, 0.4)
            ).open()


class ForgotPasswordScreen(Screen):
    def go_back(self):
        self.manager.current = 'login'

    def on_reset_button(self):
        app = App.get_running_app()
        email = self.ids.email_input.text.strip()
        new_password = self.ids.new_password_input.text
        confirm_new_password = self.ids.confirm_new_password_input.text

        # Basic validations
        if not (email and new_password and confirm_new_password):
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('All fields required')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        if new_password != confirm_new_password:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Passwords do not match')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        if len(new_password) < 6:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Password must be at least 6 characters.')),
                size_hint=(0.6, 0.4)
            ).open()
            return

        user = get_user_by_email(email)
        if not user:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Email not found.')),
                size_hint=(0.6, 0.4)
            ).open()
            return

        pw_hash = hashlib.sha256(new_password.encode()).hexdigest()
        result = update_password(email, pw_hash)
        if result.get("success"):
            Popup(
                title=app.get_translations('Success'),
                content=Label(text=app.get_translations('Password reset successful')),
                size_hint=(0.6, 0.4)
            ).open()
            self.manager.current = 'login'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Password reset failed: ') + result.get('error', '')),
                size_hint=(0.6, 0.4)
            ).open()


class DetailsScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        # Clear fields and set hints
        if 'address_input' in self.ids:
            self.ids.address_input.text = ''
            self.ids.address_input.hint_text = app.get_translations('Enter address')
        if 'dob_input' in self.ids:
            self.ids.dob_input.text = ''
            self.ids.dob_input.hint_text = app.get_translations('YYYY-MM-DD')
            # Allow manual entry:
            self.ids.dob_input.readonly = False
        if 'religion_spinner' in self.ids:
            self.ids.religion_spinner.text = app.get_translations('Select Religion')
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self._bind_form_fields())

    def _bind_form_fields(self):
        # Bind text change events
        if 'address_input' in self.ids:
            self.ids.address_input.bind(text=self.check_form)
        if 'dob_input' in self.ids:
            self.ids.dob_input.bind(text=self.check_form)
        if 'religion_spinner' in self.ids:
            self.ids.religion_spinner.bind(text=self.check_form)
        # Initially disable Continue
        self.check_form()

    def open_date_picker(self):
        date_dialog = MDDatePicker()
        # Optionally, set year range:
        # date_dialog.min_year = 1900
        # date_dialog.max_year = datetime.now().year
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        # `value` is a datetime.date object
        # Format to YYYY-MM-DD:
        self.ids.dob_input.text = value.strftime('%Y-%m-%d')

    def on_cancel(self, instance, value):
        pass

    def check_form(self, *args):
        """Enable Continue button only if all fields filled & valid."""
        app = MDApp.get_running_app()
        address = self.ids.address_input.text.strip() if 'address_input' in self.ids else ''
        dob = self.ids.dob_input.text.strip() if 'dob_input' in self.ids else ''
        religion = self.ids.religion_spinner.text.strip() if 'religion_spinner' in self.ids else ''
        select_religion_text = app.get_translations('Select Religion')
        # Check non-empty, religion not default, and dob format roughly YYYY-MM-DD
        valid = False
        if address and dob and religion and religion != select_religion_text:
            # Quick format check: 4-2-2 digits
            try:
                datetime.strptime(dob, '%Y-%m-%d')
                valid = True
            except:
                valid = False
        btn = self.ids.get('continue_button')
        if btn:
            btn.disabled = not valid
            if valid:
                # Set orange background (RGBA). If using MDApp with theme_cls.primary_color or custom:
                # If your orange is e.g. [0.9,0.5,0.2,1], set:
                try:
                    btn.md_bg_color = [0.9, 0.5, 0.2, 1]
                except:
                    # fallback for plain Button: background_color
                    btn.background_normal = ''
                    btn.background_color = [0.9, 0.5, 0.2, 1]
            else:
                # gray out
                try:
                    btn.md_bg_color = [0.5, 0.5, 0.5, 1]
                except:
                    btn.background_normal = ''
                    btn.background_color = [0.5, 0.5, 0.5, 1]

    def submit_form(self):
        app = MDApp.get_running_app()
        address = self.ids.address_input.text.strip()
        dob = self.ids.dob_input.text.strip()
        religion = self.ids.religion_spinner.text.strip()
        select_religion_text = app.get_translations('Select Religion')
        # Re-validate
        if not (address and dob and religion and religion != select_religion_text):
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('All fields required')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        # Validate date format
        try:
            datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Invalid date format.')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        # Ensure user ID present
        if not hasattr(app, 'current_user_id') or app.current_user_id is None:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('User not found. Please login again.')),
                size_hint=(0.6, 0.4)
            ).open()
            self.manager.current = 'login'
            return
        user_id = app.current_user_id
        res = update_user_details(user_id, address, dob, religion)
        if res.get('success'):
            Popup(
                title=app.get_translations('Success'),
                content=Label(text=app.get_translations('Details saved!')),
                size_hint=(0.6, 0.4)
            ).open()
            # Navigate onward
            self.manager.current = 'map'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Could not save details: ') + res.get('error', '')),
                size_hint=(0.6, 0.4)
            ).open()

    def open_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        # value is datetime.date
        self.ids.dob_input.text = value.strftime('%Y-%m-%d')

    def on_cancel(self, instance, value):
        pass

    def submit_form(self):
        app = App.get_running_app()
        address = self.ids.address_input.text.strip()
        dob = self.ids.dob_input.text.strip()
        religion = self.ids.religion_spinner.text.strip()
        if not (address and dob and religion and religion != app.get_translations('Select Religion')):
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('All fields required')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        try:
            datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Invalid date format.')),
                size_hint=(0.6, 0.4)
            ).open()
            return
        if not hasattr(app, 'current_user_id') or app.current_user_id is None:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('User not found. Please login again.')),
                size_hint=(0.6, 0.4)
            ).open()
            self.manager.current = 'login'
            return
        user_id = app.current_user_id
        res = update_user_details(user_id, address, dob, religion)
        if res.get('success'):
            Popup(
                title=app.get_translations('Success'),
                content=Label(text=app.get_translations('Details saved!')),
                size_hint=(0.6, 0.4)
            ).open()
            # Navigate onward, e.g., to main map
            self.manager.current = 'map'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Could not save details: ') + res.get('error','')),
                size_hint=(0.6, 0.4)
            ).open()


class GuestScreen(Screen):
    def explore_as_guest(self):
        app = App.get_running_app()
        app.is_guest = True
        self.manager.current = 'map'
        Popup(
            title=app.get_translations('Guest Mode'),
            content=Label(text=app.get_translations('Exploring in guest mode with limited features')),
            size_hint=(0.7, 0.2)
        ).open()

    def go_to_signup(self):
        self.manager.current = 'signup'

    def go_back(self):
        self.manager.current = 'login'


class DivineMapsApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.locale = 'en'
        self.translations = {}
        self.current_user_id = None
        # OTP data removed entirely
        self.load_translations()

    def load_translations(self):
        base = os.path.join(os.path.dirname(__file__), 'translations')
        for loc in ('en', 'hi', 'kn'):
            path = os.path.join(base, f"{loc}.yml")
            try:
                with open(path, encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    self.translations[loc] = data
            except Exception as e:
                print(f"Error loading translations for {loc}: {e}")
                self.translations[loc] = {}

    def get_translations(self, key):
        data = self.translations.get(self.locale, {})
        if key in data:
            return data[key]
        # fallback to English
        en = self.translations.get('en', {})
        return en.get(key, key)

    def set_locale(self, locale_code):
        if locale_code in self.translations:
            self.locale = locale_code
        else:
            self.locale = 'en'
        # Refresh screens:
        if hasattr(self, 'root') and self.root:
            for screen in self.root.screens:
                if hasattr(screen, 'on_pre_enter'):
                    try:
                        screen.on_pre_enter()
                    except:
                        pass

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(DetailsScreen(name='details'))
        sm.add_widget(TermsScreen(name='terms'))
        sm.add_widget(ForgotPasswordScreen(name='forgot'))
        sm.add_widget(PrivacyScreen(name='privacy'))
        sm.add_widget(GuestScreen(name='guest'))
        # Add MapScreen(name='map'), AdminScreen, etc.
        return sm


if __name__ == '__main__':
    DivineMapsApp().run()