"""
SymptomCard
-----------
A small reusable widget that displays a single symptom name
with a green leaf bullet indicator.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty


class SymptomCard(BoxLayout):
    """Displays one symptom as a labelled row."""

    symptom_name = StringProperty("")

    def __init__(self, symptom_name="", **kwargs):
        super().__init__(**kwargs)
        self.symptom_name = symptom_name
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = "36dp"
        self.spacing = "8dp"
        self.padding = ("8dp", "4dp")
