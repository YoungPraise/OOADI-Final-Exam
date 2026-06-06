"""
ui/app.py
──────────
PhytoMedApp — root Kivy application.
Assembles ScreenManager with all screens.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.metrics import dp

from ui.screens.home import HomeScreen
from ui.screens.disease_detail import DiseaseDetailScreen
from ui.screens.plant_detail import PlantDetailScreen
from ui.theme import BG_DARK


class PhytoMedApp(App):
    title = "PhytoMed"

    def build(self):
        self.icon = ""   # set to icon path if you have one

        sm = ScreenManager(transition=SlideTransition(duration=0.22))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(DiseaseDetailScreen(name="disease_detail"))
        sm.add_widget(PlantDetailScreen(name="plant_detail"))
        return sm
