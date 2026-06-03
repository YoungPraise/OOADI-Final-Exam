"""
MedicinalPlants — App Entry
Defines the Kivy App class and registers all screens with the ScreenManager.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.lang import Builder
from kivy.core.window import Window

import os

# Set a pleasant default window size for desktop
Window.size = (420, 750)

# Load all .kv layout files
KV_DIR = os.path.join(os.path.dirname(__file__), "..", "kv")


def load_kv(filename):
    path = os.path.join(KV_DIR, filename)
    if os.path.exists(path):
        Builder.load_file(path)


load_kv("home.kv")
load_kv("result.kv")
load_kv("plant_detail.kv")
load_kv("widgets.kv")

from frontend.screens.home_screen import HomeScreen          # noqa: E402
from frontend.screens.result_screen import ResultScreen      # noqa: E402
from frontend.screens.plant_detail_screen import PlantDetailScreen  # noqa: E402


class MedicinalPlantsApp(App):
    """Root application class."""

    title = "MedicinalPlants — Query & Cure"

    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ResultScreen(name="result"))
        sm.add_widget(PlantDetailScreen(name="plant_detail"))
        return sm
