# app/maps_screen.py

from kivy.uix.screenmanager import Screen
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import requests
from app.data_manager import get_user_by_id

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