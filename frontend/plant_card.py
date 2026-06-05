"""
PlantCard
---------
A tappable summary card for a medicinal plant.
Shows the plant name and a short description.
Fires an `on_tap` event with the full plant_data dict when tapped.
"""

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, DictProperty
from kivy.event import EventDispatcher


class PlantCard(ButtonBehavior, BoxLayout):
    """Tappable card showing a plant's name and short description."""

    plant_name = StringProperty("")
    plant_short_desc = StringProperty("")
    plant_data = DictProperty({})

    __events__ = ("on_tap",)

    def __init__(self, plant_data=None, **kwargs):
        super().__init__(**kwargs)

        if plant_data:
            self.plant_data = plant_data
            english = plant_data.get("english_name", "")
            latin = plant_data.get("latin_name", "")
            self.plant_name = english if english else latin
            desc = plant_data.get("description", "")
            # Truncate long descriptions for the card preview
            self.plant_short_desc = (desc[:120] + "…") if len(desc) > 120 else desc

        self.orientation = "vertical"
        self.size_hint_y = None
        self.height = "80dp"
        self.padding = ("12dp", "8dp")
        self.spacing = "4dp"

    def on_release(self):
        """Fire on_tap event when the card is released."""
        self.dispatch("on_tap", self.plant_data)

    def on_tap(self, plant_data):
        """Default handler — overridden by ResultScreen binding."""
        pass
