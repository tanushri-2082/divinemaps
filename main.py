# main.py
from kivy.config import Config
from app.app import DivineMapsApp

if __name__ == '__main__':
    # Set full screen configuration
    Config.set('graphics', 'fullscreen', 'auto')
    Config.set('graphics', 'window_state', 'maximized')
    Config.write()

    DivineMapsApp().run()