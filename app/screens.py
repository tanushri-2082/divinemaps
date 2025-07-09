# app/screens.py

import hashlib
from datetime import datetime
from mysql.connector import Error
from kivy.resources import resource_find
from kivy.properties import BooleanProperty
from kivy.uix.textinput import TextInput
from kivymd.uix.label import MDIcon
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
from .religion_data import RELIGION_CONTENT
from .data_manager import update_username
from kivy.uix.screenmanager import Screen
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import requests
from kivy.uix.screenmanager import Screen
from .data_manager import get_user_by_id
from kivy.uix.screenmanager import ScreenManager
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
import requests
from .data_manager import get_user_by_id

from .data_manager import (
    fetch_all_sites,
    register_user,
    get_user_by_email,
    update_password,
    update_user_details,
    get_user_by_id,
    submit_rating,
    submit_feedback,
    validate_user_credentials,
    fetch_sites_by_religion,
    update_user_religion,
    toggle_explore_mode,
    update_user_address
)


class LoginScreen(Screen):
    def go_back(self):
        App.get_running_app().stop()

    def on_pre_enter(self):
        self.update_translations()

    def update_translations(self):
        app = App.get_running_app()
        try:
            lang = app.locale
        except Exception:
            lang = 'en'
        hi_font = resource_find('data/fonts/NotoSansDevanagari-Regular.ttf')
        kn_font = resource_find('data/fonts/NotoSansKannada-Regular.ttf')
        en_font = resource_find('data/fonts/Roboto-Regular.ttf')
        label_font = {'hi': hi_font, 'kn': kn_font}.get(lang, en_font)
        input_font = {'hi': hi_font, 'kn': kn_font}.get(lang, en_font)

        if 'title_label' in self.ids:
            self.ids.title_label.text = app.get_translations('Divine Maps')
            self.ids.title_label.font_name = label_font
        if 'tagline_label' in self.ids:
            self.ids.tagline_label.text = app.get_translations('Spiritual Exploration Made Simple')
            self.ids.tagline_label.font_name = label_font

        if 'username_input' in self.ids:
            self.ids.username_input.hint_text = app.get_translations('Enter username')
            self.ids.username_input.font_name = input_font
        if 'password_input' in self.ids:
            self.ids.password_input.hint_text = app.get_translations('Enter password')
            self.ids.password_input.font_name = input_font

        if 'login_button' in self.ids:
            self.ids.login_button.text = app.get_translations('Login')
            self.ids.login_button.font_name = label_font

        if 'signup_label' in self.ids:
            self.ids.signup_label.text = f"[ref=signup]{app.get_translations('Sign Up')}[/ref]"
            self.ids.signup_label.font_name = label_font
        if 'forgot_label' in self.ids:
            self.ids.forgot_label.text = f"[ref=forgot]{app.get_translations('Forgot Password')}[/ref]"
            self.ids.forgot_label.font_name = label_font
        if 'guest_label' in self.ids:
            self.ids.guest_label.text = f"[ref=guest]{app.get_translations('Continue as Guest')}[/ref]"
            self.ids.guest_label.font_name = label_font

        if 'quote_label' in self.ids:
            self.ids.quote_label.text = app.get_translations('Quote')
            self.ids.quote_label.font_name = label_font

        if 'version_label' in self.ids:
            self.ids.version_label.text = app.get_translations('Version v1.0.0')
            self.ids.version_label.font_name = label_font
        if 'terms_label' in self.ids:
            self.ids.terms_label.text = f"[ref=terms]{app.get_translations('Terms')}[/ref] | [ref=privacy]{app.get_translations('Privacy')}[/ref]"
            self.ids.terms_label.font_name = label_font

    def do_login(self, username, password):
        app = App.get_running_app()
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
            app.current_user_id = user['user_id']
            self.manager.current = 'home'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Invalid credentials')),
                size_hint=(0.6, 0.4)
            ).open()

    def go_to_signup(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'signup'

    def go_to_forgot(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'forgot'

    def continue_as_guest(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'guest'

    def open_terms(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'terms'

    def open_privacy(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'privacy'

class TermsScreen(Screen):
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

class PrivacyScreen(Screen):
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

class SignUpScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
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
        if 'security_question_spinner' in self.ids:
            questions = [
                'What was the name of your first pet?',
                'What was your childhood nickname?',
                'On which street did you grow up?',
                'What was the name of your elementary school?',
                'Where did you go on your first vacation?',
                'What is the name of your best friend from childhood?',
                'What was the name of your favorite teacher?'
            ]
            self.ids.security_question_spinner.values = questions
            self.ids.security_question_spinner.text = questions[0] if questions else ''

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

    def on_signup_button(self):
        app = App.get_running_app()
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text
        confirm = self.ids.confirm_password_input.text
        security_question = self.ids.security_question_spinner.text
        security_answer = self.ids.security_answer_input.text.strip()

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

        if not security_answer:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Security answer required')),
                size_hint=(0.6, 0.4)
            ).open()
            return

        pw_hash = hashlib.sha256(password.encode()).hexdigest()


        res = register_user(username, email, pw_hash, security_question, security_answer)
        if res.get('success'):
            app.current_user_id = res['user_id']
            self.manager.transition.direction = 'left'
            self.manager.current = 'details'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=res.get('error', '')),
                size_hint=(0.6, 0.4)
            ).open()
        res = register_user(username, email, pw_hash, security_question, security_answer)

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'



class ForgotPasswordScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None  # Store user object during reset process

    def on_reset_button(self):
        app = App.get_running_app()

        if not hasattr(self, 'step') or self.step == 1:
            # Step 1: Verify email
            email = self.ids.email_input.text.strip()
            if not email:
                Popup(
                    title=app.get_translations('Error'),
                    content=Label(text=app.get_translations('Email is required')),
                    size_hint=(0.6, 0.4)
                ).open()
                return

            # Check if email exists
            user = get_user_by_email(email)
            if not user:
                Popup(
                    title=app.get_translations('Error'),
                    content=Label(text=app.get_translations('Email not found')),
                    size_hint=(0.6, 0.4)
                ).open()
                return

            # Store user and move to next step
            self.current_user = user
            self.step = 2

            # Show security question UI
            self.ids.security_question_label.text = user['security_question']
            self.ids.security_question_label.opacity = 1
            self.ids.security_answer_input.opacity = 1
            self.ids.security_answer_input.disabled = False
            return

        # Step 2: Verify security answer
        if self.step == 2:
            user_answer = self.ids.security_answer_input.text.strip().lower()
            stored_answer = self.current_user['security_answer'].lower()

            if user_answer != stored_answer:
                Popup(
                    title=app.get_translations('Error'),
                    content=Label(text=app.get_translations('Security answer incorrect')),
                    size_hint=(0.6, 0.4)
                ).open()
                return

            # Move to password reset step
            self.step = 3

            # Show password fields
            self.ids.new_password_input.opacity = 1
            self.ids.new_password_input.disabled = False
            self.ids.confirm_new_password_input.opacity = 1
            self.ids.confirm_new_password_input.disabled = False

            # Update button text
            self.ids.reset_button.text = app.get_translations('Reset Password')
            return

        # Step 3: Reset password
        if self.step == 3:
            new_password = self.ids.new_password_input.text
            confirm_new_password = self.ids.confirm_new_password_input.text

            # Validate password
            if not new_password:
                Popup(
                    title=app.get_translations('Error'),
                    content=Label(text=app.get_translations('Password is required')),
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
                    content=Label(text=app.get_translations('Password must be at least 6 characters')),
                    size_hint=(0.6, 0.4)
                ).open()
                return

            # Update password
            pw_hash = hashlib.sha256(new_password.encode()).hexdigest()
            result = update_password(self.current_user['email'], pw_hash)

            if result.get("success"):
                Popup(
                    title=app.get_translations('Success'),
                    content=Label(text=app.get_translations('Password reset successful')),
                    size_hint=(0.6, 0.4)
                ).open()
                self.manager.transition.direction = 'right'
                self.manager.current = 'login'
            else:
                Popup(
                    title=app.get_translations('Error'),
                    content=Label(text=app.get_translations('Password reset failed: ') + result.get('error', '')),
                    size_hint=(0.6, 0.4)
                ).open()

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

class DetailsScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()

        # Clear and set hints on inputs
        self.ids.address_input.text = ''
        self.ids.address_input.hint_text = app.get_translations('Enter address')
        self.ids.dob_input.text = ''
        self.ids.dob_input.hint_text = app.get_translations('YYYY-MM-DD')
        self.ids.dob_input.readonly = False

        # Initialize the religion spinner
        religions = [
            'Sikhism', 'Islam', 'Christianity',
            'Jainism', 'Hinduism', 'Buddhism',
            'Atheist', 'No Preference'
        ]
        spinner = self.ids.religion_spinner
        spinner.values = [app.get_translations(r) for r in religions]
        spinner.text   = app.get_translations('Select Religion')

        # Now bind form validation—only if that method exists
        if hasattr(self, '_bind_form_fields'):
            Clock.schedule_once(lambda dt: self._bind_form_fields())

    def _bind_form_fields(self):
        # your existing binding logic
        if 'address_input' in self.ids:
            self.ids.address_input.bind(text=self.check_form)
        if 'dob_input' in self.ids:
            self.ids.dob_input.bind(text=self.check_form)
        if 'religion_spinner' in self.ids:
            self.ids.religion_spinner.bind(text=self.check_form)
        self.check_form()

    def check_form(self, *args):
        app = MDApp.get_running_app()
        address  = self.ids.address_input.text.strip()
        dob      = self.ids.dob_input.text.strip()
        religion = self.ids.religion_spinner.text.strip()
        select_religion_text = app.get_translations('Select Religion')
        valid = False
        if address and dob and religion and religion != select_religion_text:
            try:
                datetime.strptime(dob, '%Y-%m-%d')
                valid = True
            except ValueError:
                valid = False

        btn = self.ids.get('continue_button')
        if not btn:
            return

        btn.disabled = not valid
        if valid:
            try:
                btn.md_bg_color = [0.9, 0.5, 0.2, 1]
            except AttributeError:
                btn.background_normal = ''
                btn.background_color = [0.9, 0.5, 0.2, 1]
        else:
            try:
                btn.md_bg_color = [0.5, 0.5, 0.5, 1]
            except AttributeError:
                btn.background_normal = ''
                btn.background_color = [0.5, 0.5, 0.5, 1]

    def open_date_picker(self):
        today = datetime.today()
        date_dialog = MDDatePicker(
            year=today.year,
            month=today.month,
            day=today.day
        )
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        self.ids.dob_input.text = value.strftime('%Y-%m-%d')

    def on_cancel(self, instance, value):
        pass

    def submit_form(self):
        app = App.get_running_app()
        address = self.ids.address_input.text.strip()
        # allow either slashes or hyphens, then normalize to hyphens:
        raw_dob = self.ids.dob_input.text.strip()
        dob = raw_dob.replace('/', '-')
        religion = self.ids.religion_spinner.text.strip()

        # basic required‑fields check
        if not (address and dob and religion and religion != app.get_translations('Select Religion')):
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('All fields required')),
                size_hint=(0.6, 0.4)
            ).open()
            return

        # date format check
        try:
            # expects YYYY‑MM‑DD after our replace()
            datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Invalid date format. Use YYYY‑MM‑DD or YYYY/MM/DD')),
                size_hint=(0.6, 0.4)
            ).open()
            return

        # ensure user is still logged in
        if not getattr(app, 'current_user_id', None):
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
            self.manager.current = 'home'
        else:
            Popup(
                title=app.get_translations('Error'),
                content=Label(text=app.get_translations('Could not save details: ') + res.get('error', '')),
                size_hint=(0.6, 0.4)
            ).open()

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'signup'
class GuestScreen(Screen):
    def explore_as_guest(self):
        app = App.get_running_app()
        app.is_guest = True
        self.manager.current = 'home'
        Popup(
            title=app.get_translations('Guest Mode'),
            content=Label(text=app.get_translations('Exploring in guest mode with limited features')),
            size_hint=(0.7, 0.2)
        ).open()

    def go_to_signup(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'signup'

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

class HomeScreen(Screen):
    def get_translations(self, key):
        app = App.get_running_app()
        return app.get_translations(key)

    def go_to_settings(self, *args):
        self.manager.current = 'settings'

    def go_to_favorites(self, *args):
        # Replace with actual screen or popup
        print("Favorites clicked")

    def go_to_planner(self, *args):
        # Replace with actual screen or popup
        print("Planner clicked")

    def go_to_log(self, *args):
        # Replace with actual screen or popup
        print("Log clicked")

    def show_user_profile(self):
        from .data_manager import get_user_by_id
        app = App.get_running_app()

        if not hasattr(app, 'current_user_id') or not app.current_user_id:
            self.show_popup("Error", "User not logged in")
            return

        user = get_user_by_id(app.current_user_id)
        if not user:
            self.show_popup("Error", "Could not fetch user info")
            return

        scroll = ScrollView(size_hint=(1, 1))
        inner = BoxLayout(orientation='vertical', size_hint_y=None, padding=[30, 20, 30, 20], spacing=20)
        inner.bind(minimum_height=inner.setter('height'))

        details = [
            f"Username: {user.get('username')}",
            f"Email: {user.get('email')}",
            f"Address: {user.get('address') or 'N/A'}",
            f"DOB: {user.get('dob') or 'N/A'}",
            f"Religion: {user.get('religion') or 'N/A'}",
            f"Role: {user.get('role') or 'User'}",
        ]

        for line in details:
            lbl = Label(
                text=line,
                size_hint_y=None,
                height=40,
                halign='left',
                valign='middle',
                font_size='18sp'
            )
            lbl.bind(size=lambda label, _: setattr(label, 'text_size', (label.width, None)))
            inner.add_widget(lbl)

        scroll.add_widget(inner)

        avatar = MDIcon(
            icon="account-circle",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_size="96sp",
            size_hint=(1, None),
            height=120
        )

        close_btn = Button(
            text="Close",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            font_size='18sp'
        )

        main = BoxLayout(orientation='vertical', spacing=10, padding=10)
        main.add_widget(avatar)
        main.add_widget(scroll)
        main.add_widget(close_btn)

        popup = Popup(
            title="User Profile",
            content=main,
            size_hint=(0.7, 0.7),
            auto_dismiss=False
        )

        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def go_back(self):
        app = App.get_running_app()
        if app.current_user_id:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'
        else:
            self.manager.current = 'login'

class ReligionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_religion = 'No Preference'
        self.menu = None

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if hasattr(app, 'current_user_id') and app.current_user_id:
            user = get_user_by_id(app.current_user_id)
            if user:
                self.current_religion = user.get('religion', 'No Preference')
        self.update_content()
        self.update_translations()

    def update_translations(self):
        app = App.get_running_app()
        if 'title_label' in self.ids:
            self.ids.title_label.text = app.get_translations('Religious Information')
        if 'change_button' in self.ids:
            self.ids.change_button.text = app.get_translations('Change Religion')
        if 'settings_button' in self.ids:
            self.ids.settings_button.text = app.get_translations('Settings')

    def update_content(self):
        from .data_manager import fetch_sites_by_religion
        app = App.get_running_app()
        content_label = self.ids.content_label

        # Get the content from the separate module
        religion_content = RELIGION_CONTENT.get(
            self.current_religion,
            f"Information for {self.current_religion} is not available."
        )

        # Add nearby places information
        sites = fetch_sites_by_religion(self.current_religion)
        if sites:
            religion_content += "\n\nNearby Places of Worship:\n"
            for site in sites:
                religion_content += f"\n{site['name']}\n"
                religion_content += f"Location: {site['location']}\n"
                religion_content += f"Description: {site['description']}\n"
                if site.get('entry_fee'):
                    religion_content += f"Entry: {site['entry_fee']}\n"

        content_label.text = religion_content
    def open_religion_menu(self):
        app = App.get_running_app()
        religions = [
            'Sikhism', 'Islam', 'Christianity',
            'Jainism', 'Hinduism', 'Buddhism',
            'Atheist', 'No Preference'
        ]

        menu_items = [
            {
                "text": app.get_translations(religion),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=religion: self.change_religion(x),
            } for religion in religions
        ]

        if self.menu:
            self.menu.dismiss()

        self.menu = MDDropdownMenu(
            caller=self.ids.change_button,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def change_religion(self, new_religion):
        app = App.get_running_app()
        if hasattr(app, 'current_user_id') and app.current_user_id:
            result = update_user_religion(app.current_user_id, new_religion)
            if result.get('success'):
                self.current_religion = new_religion
                self.update_content()
                self.show_popup(
                    app.get_translations('Success'),
                    app.get_translations('Religion updated')
                )
            else:
                self.show_popup(
                    app.get_translations('Error'),
                    app.get_translations('Failed to update religion')
                )

    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.6, 0.4)
        ).open()

    def go_back(self):
        app = App.get_running_app()
        if app.current_user_id:
            self.manager.transition.direction = 'right'
            self.manager.current = 'religion'
        else:
            self.manager.current = 'login'

class SettingsScreen(Screen):
    explore_mode = BooleanProperty(False)

    def on_pre_enter(self):
        app = App.get_running_app()
        if hasattr(app, 'current_user_id') and app.current_user_id:
            user = get_user_by_id(app.current_user_id)
            if user:
                self.explore_mode = user.get('explore_mode', False)
                self.ids.explore_mode_toggle.state = 'down' if self.explore_mode else 'normal'
                self.ids.explore_mode_toggle.text = f'Explore Mode: {"ON" if self.explore_mode else "OFF"}'

    def toggle_explore_mode(self, state):
        self.explore_mode = state == 'down'
        self.ids.explore_mode_toggle.text = f'Explore Mode: {"ON" if self.explore_mode else "OFF"}'

        app = App.get_running_app()
        if hasattr(app, 'current_user_id') and app.current_user_id:
            result = toggle_explore_mode(app.current_user_id, self.explore_mode)
            if result.get('success'):
                pass  # Successfully updated
            else:
                self.show_popup("Error", result.get('error', 'Failed to update explore mode'))

    def show_address_dialog(self):
        app = App.get_running_app()
        current_address = ""
        if hasattr(app, 'current_user_id') and app.current_user_id:
            user = get_user_by_id(app.current_user_id)
            if user:
                current_address = user.get('address') or ''

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        address_input = TextInput(
            hint_text='Enter your full address',
            text=current_address or '',
            multiline=True,
            size_hint_y=0.7
        )

        content.add_widget(address_input)

        dialog = Popup(
            title='Change Address',
            content=content,
            size_hint=(0.8, 0.5))

        def save_address(instance):
            new_address = address_input.text.strip()
            if not new_address:
                self.show_popup("Error", "Address cannot be empty")
                return

            if hasattr(app, 'current_user_id') and app.current_user_id:
                print(f"Attempting to update address for user_id={app.current_user_id} with: {new_address}")
                result = update_user_address(app.current_user_id, new_address)
                print(f"Update result: {result}")

                if result.get('success'):
                    self.show_popup("Success", "Address updated successfully")
                    dialog.dismiss()
                else:
                    self.show_popup("Error", result.get('error', 'Failed to update address'))

        buttons = BoxLayout(spacing=5, size_hint_y=0.2)
        buttons.add_widget(Button(text='Cancel', on_release=dialog.dismiss))
        buttons.add_widget(Button(text='Save', on_release=save_address))

        content.add_widget(buttons)
        dialog.open()

    def show_username_dialog(self):
        app = App.get_running_app()
        user = get_user_by_id(app.current_user_id)
        if not user:
            self.show_popup("Error", "User not found")
            return

        # Build the dialog content
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        # Show security question
        content.add_widget(Label(text=user['security_question'], size_hint_y=None, height=30))
        answer_input = TextInput(hint_text='Your answer', multiline=False, size_hint_y=None, height=40)
        content.add_widget(answer_input)

        # Then new username field
        content.add_widget(Label(text='New username:', size_hint_y=None, height=30))
        username_input = TextInput(multiline=False, size_hint_y=None, height=40)
        content.add_widget(username_input)

        dialog = Popup(title='Change Username', content=content, size_hint=(0.8, 0.6))

        def on_save(instance):
            # 1. verify answer
            if answer_input.text.strip().lower() != user['security_answer'].lower():
                self.show_popup("Error", "Security answer incorrect")
                return
            # 2. perform update
            new_username = username_input.text.strip()
            if not new_username:
                self.show_popup("Error", "Username cannot be empty")
                return
            from .data_manager import DataManager
            sql = "UPDATE users SET username = %s WHERE user_id = %s"
            res = DataManager._execute_update(sql, (new_username, app.current_user_id))
            if res.get('success'):
                self.show_popup("Success", "Username updated")
                dialog.dismiss()
            else:
                self.show_popup("Error", res.get('error', 'Failed to update username'))

        # Save / Cancel buttons
        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_row.add_widget(Button(text='Cancel', on_release=dialog.dismiss))
        btn_row.add_widget(Button(text='Save', on_release=on_save))
        content.add_widget(btn_row)
        dialog.open()

        def update_username(instance):
            new_username = username_input.text.strip()
            app = App.get_running_app()
            user_id = getattr(app, 'current_user_id', None)
            if not (new_username and user_id):
                dialog.dismiss()
                return

            # Call your DataManager method instead of raw SQL
            result = update_user_details(user_id, address=None, dob_str=None, religion=None)
            # (You may want to add a dedicated DataManager.update_username method; here's inline example:)
            from .data_manager import DataManager
            sql = "UPDATE users SET username = %s WHERE user_id = %s"
            result = DataManager._execute_update(sql, (new_username, user_id))

            if result.get('success'):
                self.show_popup("Success", "Username updated successfully")
                dialog.dismiss()
            else:
                self.show_popup("Error", result.get('error', 'Failed to update username'))
                dialog.dismiss()

    def show_password_dialog(self):
        app = App.get_running_app()
        user = get_user_by_id(app.current_user_id)
        if not user:
            self.show_popup("Error", "User not found")
            return

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        # Ask security question first
        content.add_widget(Label(text=user['security_question'], size_hint_y=None, height=30))
        answer_input = TextInput(hint_text='Your answer', multiline=False, size_hint_y=None, height=40)
        content.add_widget(answer_input)

        # Then current + new passwords
        content.add_widget(Label(text='Current password:', size_hint_y=None, height=30))
        current_pw = TextInput(password=True, multiline=False, size_hint_y=None, height=40)
        content.add_widget(current_pw)

        content.add_widget(Label(text='New password:', size_hint_y=None, height=30))
        new_pw = TextInput(password=True, multiline=False, size_hint_y=None, height=40)
        content.add_widget(new_pw)

        content.add_widget(Label(text='Confirm new password:', size_hint_y=None, height=30))
        confirm_pw = TextInput(password=True, multiline=False, size_hint_y=None, height=40)
        content.add_widget(confirm_pw)

        dialog = Popup(title='Change Password', content=content, size_hint=(0.8, 0.7))

        def on_update(instance):
            # 1. security answer
            if answer_input.text.strip().lower() != user['security_answer'].lower():
                self.show_popup("Error", "Security answer incorrect")
                return
            # 2. check current pw
            curr_hash = hashlib.sha256(current_pw.text.encode()).hexdigest()
            valid = validate_user_credentials(user['username'], curr_hash)
            if not valid:
                self.show_popup("Error", "Current password incorrect")
                return
            # 3. new passwords match + length
            if len(new_pw.text) < 6 or new_pw.text != confirm_pw.text:
                self.show_popup("Error", "New passwords must match and be ≥6 chars")
                return
            # 4. update
            new_hash = hashlib.sha256(new_pw.text.encode()).hexdigest()
            res = update_password(user['email'], new_hash)
            if res.get('success'):
                self.show_popup("Success", "Password updated")
                dialog.dismiss()
            else:
                self.show_popup("Error", res.get('error','Failed to update password'))

        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_row.add_widget(Button(text='Cancel', on_release=dialog.dismiss))
        btn_row.add_widget(Button(text='Update', on_release=on_update))
        content.add_widget(btn_row)
        dialog.open()


        def update_password(instance):
            if not new_pw.text or len(new_pw.text) < 6:
                self.show_popup("Error", "Password must be at least 6 characters")
                return

            if new_pw.text != confirm_pw.text:
                self.show_popup("Error", "Passwords don't match")
                return

            app = App.get_running_app()
            if hasattr(app, 'current_user_id') and app.current_user_id:
                current_hash = hashlib.sha256(current_pw.text.encode()).hexdigest()
                user = validate_user_credentials(app.current_user.username, current_hash)
                if not user:
                    self.show_popup("Error", "Current password is incorrect")
                    return

                new_hash = hashlib.sha256(new_pw.text.encode()).hexdigest()
                result = update_password(app.current_user.email, new_hash)
                if result.get('success'):
                    self.show_popup("Success", "Password updated successfully")
                    dialog.dismiss()
                else:
                    self.show_popup("Error", result.get('error', 'Failed to update password'))

        content.add_widget(Button(text='Update', on_release=update_password))
        dialog.open()

    def rate_app(self, stars):
        app = App.get_running_app()
        if not hasattr(app, 'current_user_id') or not app.current_user_id:
            self.show_popup("Error", "Please login to rate the app")
            return

        result = submit_rating(app.current_user_id, stars)
        if result.get('success'):
            self.show_popup("Thank You!", f"Thanks for your {stars} star rating!")
        else:
            self.show_popup("Error", "Failed to submit rating. Please try again.")

    def go_back(self):
        # if the user is logged in, go back to home; otherwise to login
        app = App.get_running_app()
        if app.current_user_id:
            self.manager.transition.direction = 'right'
            self.manager.current = 'home'
        else:
            self.manager.current = 'login'

    def submit_feedback(self):
        feedback = self.ids.feedback_input.text.strip()
        if not feedback:
            self.show_popup("Error", "Please enter feedback text")
            return

        app = App.get_running_app()
        if not hasattr(app, 'current_user_id') or not app.current_user_id:
            self.show_popup("Error", "Please login to submit feedback")
            return

        result = submit_feedback(app.current_user_id, feedback)
        if result.get('success'):
            self.ids.feedback_input.text = ''
            self.show_popup("Thank You!", "Your feedback has been submitted.")
        else:
            self.show_popup("Error", "Failed to submit feedback. Please try again.")

    def show_popup(self, title, message):
        Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.6, 0.4)
        ).open()

class HelpScreen(Screen):
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login'

class MapsScreen(Screen):
    def on_enter(self):
        print("✅ MapsScreen loaded")
        self.load_sites()
        Clock.schedule_once(self.show_map, 0.1)

        app = App.get_running_app()
        if hasattr(app, 'selected_site') and app.selected_site:
            site = app.selected_site
            self.center_lat = site['latitude']
            self.center_lon = site['longitude']
            self.zoom_level = 15
            app.selected_site = None
        else:
            self.center_lat = 12.9716  # Default: Bengaluru
            self.center_lon = 77.5946
            self.zoom_level = 10

    def show_map(self, *args):
        print("🗺️ Rendering MapView inside MapsScreen")
        self.ids.mapbox.clear_widgets()

        mapview = MapView(
            zoom=self.zoom_level,
            lat=self.center_lat,
            lon=self.center_lon
        )
        self.mapview = mapview
        self.ids.mapbox.add_widget(mapview)

        for site in self.sites:
            marker = MapMarkerPopup(lat=site['latitude'], lon=site['longitude'])
            marker.site_data = site
            marker.bind(on_release=self.show_popup)
            mapview.add_widget(marker)

    def load_sites(self):
        try:
            app = App.get_running_app()
            user = get_user_by_id(app.current_user_id) if hasattr(app, 'current_user_id') and app.current_user_id else None
            religion = user.get('religion', 'No Preference') if user else 'No Preference'
            response = requests.get(f"http://127.0.0.1:5000/get_sites?religion={religion}")
            self.sites = response.json()
        except Exception as e:
            print(f"Error fetching markers: {e}")
            self.sites = []

    def show_popup(self, marker):
        site = marker.site_data
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=f"[b]{site['name']}[/b]", markup=True))
        content.add_widget(Label(text=f"Religion: {site.get('religion', 'N/A')}"))
        content.add_widget(Label(text=f"Address: {site.get('address', 'N/A')}"))
        content.add_widget(Button(text="View Details", on_release=lambda x: self.go_to_details(site)))
        popup = Popup(
            title=site['name'],
            content=content,
            size_hint=(0.7, 0.4)
        )
        popup.open()

    def go_to_details(self, site):
        app = App.get_running_app()
        app.selected_site = site
        self.manager.current = 'site_detail'

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'


class TempleSelectionScreen(Screen):
    def on_enter(self):
        print("✅ TempleSelectionScreen loaded")
        self.load_temples()

    def load_temples(self):
        try:
            # Fetch 4 temples from the Flask API
            app = App.get_running_app()
            user = get_user_by_id(app.current_user_id) if hasattr(app, 'current_user_id') and app.current_user_id else None
            religion = user.get('religion', 'No Preference') if user else 'No Preference'
            response = requests.get(f"http://127.0.0.1:5000/get_sites?religion={religion}&limit=4")
            temples = response.json()
            self.display_temples(temples)
        except Exception as e:
            print(f"Error fetching temples: {e}")
            self.ids.temple_grid.clear_widgets()

    def display_temples(self, temples):
        grid = self.ids.temple_grid
        grid.clear_widgets()
        for temple in temples:
            button = MDRaisedButton(
                text=temple['name'],
                size_hint=(None, None),
                size=(200, 80),
                on_release=lambda x, t=temple: self.go_to_details(t)
            )
            grid.add_widget(button)

    def go_to_details(self, temple):
        app = App.get_running_app()
        app.selected_site = temple
        self.manager.current = 'site_detail'

class SiteDetailScreen(Screen):
    def on_enter(self):
        print("✅ SiteDetailScreen loaded")
        self.display_details()

    def display_details(self):
        app = App.get_running_app()
        site = app.selected_site if hasattr(app, 'selected_site') and app.selected_site else {}
        content_label = self.ids.site_content
        if site:
            details = (
                f"[b]Name:[/b] {site.get('name', 'N/A')}\n"
                f"[b]Religion:[/b] {site.get('religion', 'N/A')}\n"
                f"[b]Address:[/b] {site.get('address', 'N/A')}\n"
                f"[b]Description:[/b] {site.get('description', 'N/A')}\n"
                f"[b]Latitude:[/b] {site.get('latitude', 'N/A')}\n"
                f"[b]Longitude:[/b] {site.get('longitude', 'N/A')}"
            )
            content_label.text = details
        else:
            content_label.text = "No site selected."

    def navigate_to_map(self):
        self.manager.current = 'maps'

class SiteListScreen(Screen):
    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'home'