# main.py

import os
import hashlib
import yaml
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.resources import resource_find
from kivy.properties import BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from mysql.connector import Error
from kivymd.app import MDApp
from kivymd.uix.pickers.datepicker import MDDatePicker
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu

from kivy.config import Config
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')

from kivy.core.window import Window
Window.maximize()                   # for fullscreen

from app.data_manager import (
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
    get_connection,
    update_user_address

)

# Load KV files
Builder.load_file('ui/login.kv')
Builder.load_file('ui/signup.kv')
Builder.load_file('ui/details.kv')
Builder.load_file('ui/terms.kv')
Builder.load_file('ui/privacy.kv')
Builder.load_file('ui/forgot.kv')
Builder.load_file('ui/home.kv')
Builder.load_file('ui/guest.kv')
Builder.load_file('ui/admin.kv')
Builder.load_file('ui/settings.kv')
Builder.load_file('ui/religion.kv')

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
            self.manager.current = 'home'
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
            self.manager.current = 'home'
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
            self.manager.current = 'home'
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
        self.manager.current = 'home'
        Popup(
            title=app.get_translations('Guest Mode'),
            content=Label(text=app.get_translations('Exploring in guest mode with limited features')),
            size_hint=(0.7, 0.2)
        ).open()

    def go_to_signup(self):
        self.manager.current = 'signup'

    def go_back(self):
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
        app = App.get_running_app()
        content_label = self.ids.content_label

        if self.current_religion == 'Atheist':
            content_label.text = app.get_translations(
                'This app is designed for spiritual exploration. As an atheist, you might not find it useful. We recommend uninstalling the app.')
            return
        elif self.current_religion == 'No Preference':
            content_label.text = app.get_translations(
                'Showing information for all religions (recommended for tourists)')
            sites = fetch_sites_by_religion(None)
            if sites:
                content_label.text += "\n\n" + "\n".join([f"{site['name']} - {site['description']}" for site in sites])
            return

        religion_content = {
            'Hinduism': """
        - Hinduism is one of the world's oldest living religions, originating over 4000 years ago in the Indian subcontinent.
        - It has no single founder and is considered a way of life rather than a rigid belief system.
        - The religion encompasses a wide variety of beliefs and practices unified by concepts like Dharma (duty), Karma (action and consequence), and Moksha (liberation).
        - It teaches that the soul (Atman) is eternal and seeks union with the Supreme Reality (Brahman).
        - Reincarnation is a core belief—after death, the soul is reborn based on one’s karma.
        - Major deities include Brahma (creator), Vishnu (preserver), and Shiva (destroyer), along with goddesses like Lakshmi, Saraswati, and Durga.
        - The concept of avatars (divine incarnations) is central, such as Rama and Krishna being avatars of Vishnu.
        - Sacred texts include the Vedas, Upanishads, Bhagavad Gita, Ramayana, and Mahabharata.
        - Daily worship (puja), temple visits, chanting, and yoga are common practices.
        - Hindu festivals are vibrant and numerous, including Diwali (Festival of Lights), Holi (Festival of Colors), Navratri, Janmashtami, and Raksha Bandhan.
        - Pilgrimage to sacred places like Varanasi, Rameshwaram, and Kedarnath is highly valued.
        - Social duty (dharma) is tied to one’s stage of life and role in society.
        - Vegetarianism and non-violence are encouraged in many Hindu traditions.
        - The caste system historically influenced social structure but is increasingly challenged.
        - Hinduism promotes spiritual exploration through multiple paths: Bhakti (devotion), Jnana (knowledge), Karma (action), and Raja (meditation).
        """,

            'Islam': """
        - Islam is a monotheistic Abrahamic religion founded in the 7th century CE in Mecca by Prophet Muhammad.
        - Muslims believe in one God, Allah, who is compassionate, all-powerful, and just.
        - The Qur'an is Islam’s holy book, considered the literal word of God revealed to Muhammad through the angel Gabriel.
        - The Hadith (sayings of the Prophet) provide guidance on Islamic law and daily living.
        - The Five Pillars of Islam form the foundation of a Muslim’s faith and actions:
          1. Shahada – declaration of faith
          2. Salat – praying five times a day
          3. Zakat – giving charity to the poor
          4. Sawm – fasting during the month of Ramadan
          5. Hajj – pilgrimage to Mecca (once in a lifetime, if possible)
        - Muslims gather weekly on Fridays for communal prayer at a mosque.
        - Modesty in dress and behavior is emphasized; many women wear the hijab.
        - Halal dietary laws prohibit pork and alcohol and require humane slaughtering of animals.
        - Major holidays include Eid al-Fitr (celebration after Ramadan) and Eid al-Adha (Festival of Sacrifice).
        - Islam recognizes earlier prophets like Adam, Abraham, Moses, and Jesus but regards Muhammad as the final prophet.
        - Muslims believe in the Day of Judgment and eternal life in paradise or hell based on one’s deeds.
        - Community, humility, and compassion are key values.
        - Islamic art and architecture are known for their geometric patterns, calligraphy, and grand mosques.
        """,

            'Christianity': """
        - Christianity is a monotheistic religion based on the life and teachings of Jesus Christ, believed by followers to be the Son of God.
        - It originated in the 1st century CE in Judea (modern-day Israel/Palestine).
        - Christians believe Jesus was crucified, died for the sins of humanity, and was resurrected.
        - The Bible is the holy scripture, consisting of the Old Testament (shared with Judaism) and the New Testament (focused on Jesus and the early church).
        - Core beliefs include the Holy Trinity (Father, Son, Holy Spirit), salvation by grace, and eternal life through faith in Jesus.
        - Baptism and Holy Communion (Eucharist) are key sacraments in most denominations.
        - The Christian community is diverse, including branches such as Catholicism, Protestantism, and Eastern Orthodoxy.
        - Churches are places of worship and community gathering.
        - Sunday is observed as the Sabbath and a day of worship.
        - Christmas (celebrating Jesus’ birth), Good Friday (his crucifixion), and Easter (his resurrection) are major festivals.
        - Christian ethics promote love, forgiveness, charity, humility, and service to others.
        - Missionary work and spreading the message of Jesus is a common practice.
        - Christian music, art, and literature have shaped much of Western civilization.
        - The religion has around 2.3 billion followers worldwide, making it the largest religion globally.
        """,

            'Jainism': """
        - Jainism is an ancient Indian religion that emphasizes non-violence, self-discipline, and truth.
        - It was formalized by Mahavira, the 24th Tirthankara, in the 6th century BCE.
        - Jains believe in an eternal soul (jiva) that can attain liberation (moksha) by purifying itself from karma.
        - The religion strictly opposes harm to any living being, making Ahimsa (non-violence) the highest principle.
        - Jains follow strict vegetarianism, and many avoid root vegetables to prevent harming micro-organisms.
        - The main scriptures are the Agamas and other Jain texts written in Prakrit.
        - Jain monks and nuns follow severe austerities, including fasting, celibacy, and walking barefoot.
        - There are two major sects: Digambara (sky-clad) and Shwetambara (white-clad).
        - Symbols of Jainism include the hand with a wheel (Ahimsa), the Swastika, and the Jain emblem.
        - Key ethical principles include Satya (truth), Asteya (non-stealing), Brahmacharya (celibacy), and Aparigraha (non-possession).
        - Temples are beautifully decorated with marble carvings and intricate artwork.
        - Major festivals include Mahavir Jayanti (birth of Mahavira), Paryushan (spiritual reflection), and Diwali (commemorates Mahavira’s liberation).
        - Jainism does not believe in a creator god; the universe is eternal and self-regulated.
        - Liberation is achieved through knowledge, right conduct, and non-attachment.
        """,

            'Buddhism': """
        - Buddhism is a non-theistic spiritual tradition founded by Siddhartha Gautama (Buddha) in the 6th century BCE.
        - It originated in India and later spread across Asia, forming traditions like Theravāda, Mahāyāna, and Vajrayāna.
        - The core of Buddhism lies in the Four Noble Truths:
          1. Life involves suffering (dukkha)
          2. Suffering is caused by desire (tanha)
          3. There is a way to end suffering
          4. The Eightfold Path leads to the end of suffering
        - The Eightfold Path includes right understanding, thought, speech, action, livelihood, effort, mindfulness, and concentration.
        - The goal is Nirvana—a state of liberation from suffering and the cycle of rebirth (samsara).
        - Meditation, mindfulness, ethical living, and compassion are central practices.
        - Key teachings are preserved in texts like the Tripitaka and the Dhammapada.
        - Buddhists often follow precepts such as refraining from killing, stealing, lying, intoxication, and sexual misconduct.
        - Temples, monasteries, and stupas are common places of worship and practice.
        - Monks and nuns form the Sangha, a spiritual community dedicated to monastic life.
        - Major festivals include Vesak (Buddha’s birth, enlightenment, and death), Magha Puja, and Asalha Puja.
        - Buddhism does not promote belief in a creator god but focuses on personal spiritual progress.
        - The lotus flower and the Dharma wheel are common symbols representing purity and the path.
        """,

            'Sikhism': """
        - Sikhism is a monotheistic religion founded by Guru Nanak in the 15th century in Punjab, India.
        - It emphasizes devotion to one God, honest living, equality of all people, and selfless service.
        - The teachings of ten Gurus are compiled in the Guru Granth Sahib, the eternal Guru and holy scripture.
        - The core beliefs include Naam Japna (remembering God), Kirat Karni (righteous living), and Vand Chakna (sharing with others).
        - Sikhism rejects rituals, caste distinctions, and idol worship.
        - The Five Ks are articles of faith worn by initiated Sikhs:
          1. Kesh – uncut hair
          2. Kara – steel bracelet
          3. Kanga – wooden comb
          4. Kachera – cotton undergarment
          5. Kirpan – ceremonial sword
        - Sikhs worship at Gurdwaras, where the Guru Granth Sahib is recited and respected.
        - A key feature of Gurdwaras is the Langar—a free communal meal open to all.
        - Sikh festivals include Guru Nanak Jayanti (birth anniversary of Guru Nanak) and Baisakhi (harvest and Khalsa foundation day).
        - Sikhism encourages meditation on God's name, community service, humility, and resilience.
        - It believes in the concept of reincarnation and the ultimate union of the soul with Waheguru (God).
        - Turban-wearing is an important cultural and spiritual identity marker for Sikhs.
        - The religion has a strong tradition of defending justice and standing against oppression.
        """
        }.get(self.current_religion, '')

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
        self.manager.current = 'home'



class SettingsScreen(Screen):
    explore_mode = BooleanProperty(False)

    def on_pre_enter(self):
        # Load current settings
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

        # Save to database
        app = App.get_running_app()
        if hasattr(app, 'current_user_id') and app.current_user_id:
            result = toggle_explore_mode(app.current_user_id, self.explore_mode)
            if result.get('success'):
                pass  # Successfully updated
            else:
                self.show_popup("Error", result.get('error', 'Failed to update explore mode'))

    def show_address_dialog(self):
        app = App.get_running_app()

        # Get current address if available
        current_address = ""
        if hasattr(app, 'current_user_id') and app.current_user_id:
            user = get_user_by_id(app.current_user_id)
            if user:
                current_address = user.get('address') or ''

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        address_input = TextInput(
            hint_text='Enter your full address',
            text=current_address or '',  # ✅ this avoids the crash
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
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text='Enter new username:'))
        username_input = TextInput(multiline=False)
        content.add_widget(username_input)

        dialog = Popup(
            title='Change Username',
            content=content,
            size_hint=(0.8, 0.4)
        )

        def update_username(instance):
            new_username = username_input.text.strip()
            if new_username:
                app = App.get_running_app()
                if hasattr(app, 'current_user_id') and app.current_user_id:
                    conn = get_connection()
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT user_id FROM users WHERE username = %s AND user_id != %s",
                            (new_username, app.current_user_id)
                        )
                        if cursor.fetchone():
                            self.show_popup("Error", "Username already taken")
                            return

                        cursor.execute(
                            "UPDATE users SET username = %s WHERE user_id = %s",
                            (new_username, app.current_user_id)
                        )
                        conn.commit()
                        self.show_popup("Success", "Username updated successfully")
                    except Error as e:
                        self.show_popup("Error", f"Failed to update username: {str(e)}")
                    finally:
                        if conn and conn.is_connected():
                            conn.close()
            dialog.dismiss()

        content.add_widget(Button(text='Update', on_release=update_username))
        dialog.open()

    def show_password_dialog(self):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text='Current password:'))
        current_pw = TextInput(password=True, multiline=False)
        content.add_widget(current_pw)

        content.add_widget(Label(text='New password:'))
        new_pw = TextInput(password=True, multiline=False)
        content.add_widget(new_pw)

        content.add_widget(Label(text='Confirm new password:'))
        confirm_pw = TextInput(password=True, multiline=False)
        content.add_widget(confirm_pw)

        dialog = Popup(
            title='Change Password',
            content=content,
            size_hint=(0.8, 0.6)
        )

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
        self.manager.current = 'home'

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


class DivineMapsApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.locale = 'en'
        self.translations = {}
        self.current_user_id = None
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
        en = self.translations.get('en', {})
        return en.get(key, key)

    def set_locale(self, locale_code):
        if locale_code in self.translations:
            self.locale = locale_code
        else:
            self.locale = 'en'
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
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(ReligionScreen(name='religion'))
        return sm


if __name__ == '__main__':
    DivineMapsApp().run()