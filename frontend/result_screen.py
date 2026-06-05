"""
ResultScreen
------------
Displays the disease description, prevention advice, symptom list,
and a scrollable list of PlantCard widgets.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ListProperty

from frontend.widgets.plant_card import PlantCard
from frontend.widgets.symptom_card import SymptomCard


class ResultScreen(Screen):
    """Shows search results for a disease."""

    disease_name = StringProperty("")
    disease_description = StringProperty("")
    disease_prevention = StringProperty("")
    symptoms = ListProperty([])

    def load_result(self, result: dict):
        """
        Populate the screen with data from search_service.search().

        Expected result structure:
        {
            "disease": {
                "name": str,
                "description": str,
                "prevention": str,
            },
            "symptoms": [{"name": str}, ...],
            "plants": [
                {
                    "id": int,
                    "latin_name": str,
                    "english_name": str,
                    "description": str,
                    "cameroon_location": str,
                    "application_steps": str,
                    "precautions": str,
                    "toxicity": str,
                    "part_of_plant": str,
                    "preparation_method": str,
                },
                ...
            ],
        }
        """
        disease = result.get("disease", {})
        self.disease_name = disease.get("name", "Unknown")
        self.disease_description = disease.get("description", "")
        self.disease_prevention = disease.get("prevention", "")

        # --- Symptoms ---
        symptoms_list = result.get("symptoms", [])
        symptom_container = self.ids.symptom_container
        symptom_container.clear_widgets()

        if symptoms_list:
            for symptom in symptoms_list:
                card = SymptomCard(symptom_name=symptom.get("name", ""))
                symptom_container.add_widget(card)
        else:
            from kivy.uix.label import Label
            symptom_container.add_widget(
                Label(
                    text="No symptoms listed.",
                    size_hint_y=None,
                    height="32dp",
                    color=(0.5, 0.5, 0.5, 1),
                )
            )

        # --- Plant Cards ---
        plants_list = result.get("plants", [])
        plants_container = self.ids.plants_container
        plants_container.clear_widgets()

        if plants_list:
            for plant in plants_list:
                card = PlantCard(plant_data=plant)
                card.bind(on_tap=self._on_plant_tap)
                plants_container.add_widget(card)
        else:
            from kivy.uix.label import Label
            plants_container.add_widget(
                Label(
                    text="No medicinal plants found for this illness.",
                    size_hint_y=None,
                    height="40dp",
                    color=(0.5, 0.5, 0.5, 1),
                )
            )

    def _on_plant_tap(self, plant_card, plant_data):
        """Navigate to PlantDetailScreen with the tapped plant's data."""
        detail_screen = self.manager.get_screen("plant_detail")
        detail_screen.load_plant(plant_data)
        self.manager.current = "plant_detail"

    def go_home(self):
        """Return to the HomeScreen."""
        self.manager.current = "home"
