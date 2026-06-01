# frontend/screens/home_screen.py
# HomeScreen — the search input screen.
# User types an illness name and presses Search.

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock


class HomeScreen(Screen):
    """
    The first screen the user sees.
    Contains a search bar and a Search button.
    On search, calls the backend search_service and
    passes results to ResultScreen.
    """

    def on_enter(self):
        """Called every time this screen becomes active."""
        # Clear previous search and any error message
        self.ids.search_input.text = ""
        self.ids.error_label.text = ""
        # Auto-focus the search box after a short delay
        Clock.schedule_once(lambda dt: self.ids.search_input.focus_next(), 0.3)

    def on_search(self):
        """Triggered when the user presses Search or hits Enter."""
        illness_name = self.ids.search_input.text.strip()

        # Guard: don't search if the field is empty
        if not illness_name:
            self.ids.error_label.text = "⚠  Please enter an illness name."
            return

        # Clear any previous error
        self.ids.error_label.text = ""

        # Call the backend search service
        try:
            from backend.search_service import search
            result = search(illness_name)
        except Exception as e:
            self.ids.error_label.text = f"⚠  Backend error: {str(e)}"
            return

        # If nothing was found, show a message and stay on this screen
        if not result:
            self.ids.error_label.text = f"No results found for '{illness_name}'."
            return

        # Pass the result to ResultScreen and navigate there
        result_screen = self.manager.get_screen('result')
        result_screen.load_data(result)
        self.manager.current = 'result'
        self.manager.transition.direction = 'left'