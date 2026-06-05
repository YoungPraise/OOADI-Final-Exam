"""
PlantDetailScreen
-----------------
Shows the complete details of a single medicinal plant:
latin name, English name, location in Cameroon, preparation steps,
precautions, and toxicity information.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


class PlantDetailScreen(Screen):
    """Full detail view for one medicinal plant."""

    latin_name = StringProperty("")
    english_name = StringProperty("")
    description = StringProperty("")
    cameroon_location = StringProperty("")
    part_of_plant = StringProperty("")
    preparation_method = StringProperty("")
    application_steps = StringProperty("")
    precautions = StringProperty("")
    toxicity = StringProperty("")

    def load_plant(self, plant_data: dict):
        """
        Populate the screen with plant data.

        Expected plant_data keys:
            latin_name, english_name, description, cameroon_location,
            part_of_plant, preparation_method, application_steps,
            precautions, toxicity
        """
        self.latin_name = plant_data.get("latin_name", "")
        self.english_name = plant_data.get("english_name", "")
        self.description = plant_data.get("description", "")
        self.cameroon_location = plant_data.get("cameroon_location", "")
        self.part_of_plant = plant_data.get("part_of_plant", "")
        self.preparation_method = plant_data.get("preparation_method", "")
        self.application_steps = plant_data.get("application_steps", "")
        self.precautions = plant_data.get("precautions", "")
        self.toxicity = plant_data.get("toxicity", "")

    def go_back(self):
        """Return to the ResultScreen."""
        self.manager.current = "result"
