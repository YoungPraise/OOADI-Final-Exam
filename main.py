# main.py
# Entry point for the MedicinalPlants application.
# Run this file to start the app: python main.py

import os
import sys

# Add the project root to the Python path so all imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set the Kivy window title before importing Kivy modules
os.environ["KIVY_NO_CONSOLELOG"] = "1"  # Cleaner terminal output

from frontend.app import MedicinalPlantsApp

if __name__ == "__main__":
    MedicinalPlantsApp().run()