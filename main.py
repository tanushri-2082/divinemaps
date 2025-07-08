# main.py

from app.app import DivineMapsApp
from kivy.config import Config

if __name__ == '__main__':
    # Set full screen configuration
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()

    DivineMapsApp().run()


