# frontend/app.py
# The Kivy App class — sets up the ScreenManager and loads all screens.

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.lang import Builder
from kivy.core.window import Window
import os

# Load all .kv layout files
KV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kv')

Builder.load_file(os.path.join(KV_DIR, 'home.kv'))
Builder.load_file(os.path.join(KV_DIR, 'result.kv'))
Builder.load_file(os.path.join(KV_DIR, 'plant_detail.kv'))

# Import all screens
from frontend.screens.home_screen import HomeScreen
from frontend.screens.result_screen import ResultScreen
from frontend.screens.plant_detail_screen import PlantDetailScreen


class MedicinalPlantsApp(App):
    """
    Main application class.
    Kivy looks for a file called medicinalplants.kv automatically —
    we handle layout manually via Builder.load_file() above instead.
    """

    def build(self):
        # Set window background color (dark green, earthy feel)
        Window.clearcolor = (0.08, 0.12, 0.08, 1)

        # Set up the screen manager with a smooth slide transition
        sm = ScreenManager(transition=SlideTransition())

        # Register all screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(PlantDetailScreen(name='plant_detail'))

        # Start on the home screen
        sm.current = 'home'

        return sm

    def get_application_name(self):
        return "MedicinalPlants"