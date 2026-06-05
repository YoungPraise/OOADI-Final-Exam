# frontend/screens/plant_detail_screen.py
# PlantDetailScreen — shows full details of a single plant.
# Receives data from ResultScreen when a plant card is tapped.

from kivy.uix.screenmanager import Screen


class PlantDetailScreen(Screen):
    """
    Displays all available information about one medicinal plant:
    - Common name
    - Local name
    - Parts used
    - Preparation method
    - Dosage
    - Side effects
    - Scientific name
    """

    def load_data(self, plant: dict):
        """
        Called by ResultScreen before navigating here.
        Populates all the labels with plant data.

        Expected keys in plant dict:
            name, local_name, parts_used, preparation,
            dosage, side_effects, scientific_name
        """
        self.ids.plant_name_label.text    = plant.get('name', 'Unknown Plant')
        self.ids.local_name_label.text    = plant.get('local_name', 'N/A')
        self.ids.parts_used_label.text    = plant.get('parts_used', 'N/A')
        self.ids.preparation_label.text   = plant.get('preparation', 'N/A')
        self.ids.dosage_label.text        = plant.get('dosage', 'N/A')
        self.ids.side_effects_label.text  = plant.get('side_effects', 'None reported')
        self.ids.scientific_name_label.text = plant.get('scientific_name', '')

    def on_enter(self):
        """Called every time this screen becomes active."""
        pass

    def go_back(self):
        """Navigate back to the Result screen."""
        self.manager.current = 'result'
        self.manager.transition.direction = 'right'