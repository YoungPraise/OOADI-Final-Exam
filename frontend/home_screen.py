"""
HomeScreen
----------
The first screen the user sees.
Contains a search bar and a Search button.
On search, calls search_service and navigates to ResultScreen.
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty


class HomeScreen(Screen):
    """Search input screen."""

    status_message = StringProperty("")

    def on_search(self):
        """Called when the user presses the Search button."""
        query = self.ids.search_input.text.strip()

        if not query:
            self.status_message = "Please enter an illness name to search."
            return

        self.status_message = "Searching…"

        try:
            # Import here to avoid circular imports at module load time
            from backend.search_service import search

            result = search(query)

            if result is None:
                self.status_message = (
                    f'No results found for "{query}". '
                    "Try a different illness name."
                )
                return

            # Pass data to ResultScreen then navigate
            result_screen = self.manager.get_screen("result")
            result_screen.load_result(result)
            self.status_message = ""
            self.manager.current = "result"

        except Exception as exc:  # pragma: no cover
            self.status_message = f"Error: {exc}"
