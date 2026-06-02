# frontend/screens/result_screen.py
# ResultScreen — displays the illness info and a list of plant remedy cards.
# Each card is tappable and opens the PlantDetailScreen.

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp


class TappableCard(ButtonBehavior, BoxLayout):
    """
    A plant card that responds to taps.
    ButtonBehavior gives BoxLayout the ability to detect on_press.
    """
    pass


class ResultScreen(Screen):
    """
    Shows the illness name, a short description,
    and a scrollable list of plant remedy cards.
    Tapping a card navigates to PlantDetailScreen.
    """

    # Stores the current result data so we can reference it on card tap
    _current_result = None

    def load_data(self, result: dict):
        """
        Called by HomeScreen before navigating here.
        Populates illness info and builds plant cards dynamically.

        Expected result dict structure:
        {
            'illness': 'Malaria',
            'description': 'A mosquito-borne disease...',
            'plants': [
                {
                    'name': 'Neem',
                    'scientific_name': 'Azadirachta indica',
                    'local_name': 'Dongoyaro',
                    'parts_used': 'Leaves, Bark',
                    'preparation': 'Boil leaves in water...',
                    'dosage': 'Twice daily...',
                    'side_effects': 'May cause nausea...'
                },
                ...
            ]
        }
        """
        self._current_result = result

        # Set illness title and description
        self.ids.illness_title.text = result.get('illness', 'Results')
        self.ids.illness_description.text = result.get('description', '')

        # Update the plants found count
        plants = result.get('plants', [])
        count = len(plants)
        self.ids.plants_found_label.text = (
            f"{count} plant{'s' if count != 1 else ''} found"
        )

        # Clear any previously loaded cards
        self.ids.cards_container.clear_widgets()

        # Build a card for each plant
        for plant in plants:
            self._add_plant_card(plant)

    def _add_plant_card(self, plant: dict):
        """Creates one tappable plant card and adds it to the scroll list."""

        card = TappableCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=dp(15),
            spacing=dp(6)
        )

        # Style the card background via canvas
        from kivy.graphics import Color, RoundedRectangle, Line
        with card.canvas.before:
            Color(0.12, 0.2, 0.12, 1)
            card._bg = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[dp(10)]
            )
            Color(0.2, 0.5, 0.2, 0.4)
            card._border = Line(
                rounded_rectangle=(
                    card.x, card.y, card.width, card.height, dp(10)
                ),
                width=1.2
            )

        # Update canvas when card moves or resizes
        card.bind(
            pos=self._update_card_canvas,
            size=self._update_card_canvas
        )

        # Plant name
        name_label = Label(
            text=plant.get('name', 'Unknown'),
            font_size=dp(17),
            bold=True,
            color=(0.4, 0.85, 0.4, 1),
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        name_label.bind(size=lambda l, s: setattr(l, 'text_size', s))

        # Scientific name
        sci_label = Label(
            text=plant.get('scientific_name', ''),
            font_size=dp(13),
            italic=True,
            color=(0.5, 0.75, 0.5, 0.8),
            halign='left',
            size_hint_y=None,
            height=dp(22)
        )
        sci_label.bind(size=lambda l, s: setattr(l, 'text_size', s))

        # Parts used
        parts_label = Label(
            text=f"Parts used: {plant.get('parts_used', 'N/A')}",
            font_size=dp(12),
            color=(0.6, 0.8, 0.6, 0.7),
            halign='left',
            size_hint_y=None,
            height=dp(20)
        )
        parts_label.bind(size=lambda l, s: setattr(l, 'text_size', s))

        card.add_widget(name_label)
        card.add_widget(sci_label)
        card.add_widget(parts_label)

        # On tap — navigate to PlantDetailScreen with this plant's data
        card.bind(on_press=lambda instance, p=plant: self._open_plant(p))

        self.ids.cards_container.add_widget(card)

    def _update_card_canvas(self, card, *args):
        """Keeps the card background in sync when it resizes."""
        card._bg.pos = card.pos
        card._bg.size = card.size
        card._border.rounded_rectangle = (
            card.x, card.y, card.width, card.height, dp(10)
        )

    def _open_plant(self, plant: dict):
        """Navigates to PlantDetailScreen with the selected plant's data."""
        detail_screen = self.manager.get_screen('plant_detail')
        detail_screen.load_data(plant)
        self.manager.current = 'plant_detail'
        self.manager.transition.direction = 'left'

    def go_back(self):
        """Navigate back to HomeScreen."""
        self.manager.current = 'home'
        self.manager.transition.direction = 'right'

    def on_leave(self):
        """Clear cards when leaving to free up memory."""
        self.ids.cards_container.clear_widgets()