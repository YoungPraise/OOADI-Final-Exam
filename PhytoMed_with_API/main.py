"""
PhytoMed — Medicinal Plants & Disease Reference App
Entry point. Run with: python main.py

Architecture:
  main.py  →  Kivy UI  →  ApiClient (HTTP)  →  FastAPI server  →  DatabaseService (SQLite)

Start the server first:
    python -m api.server
Then start the app:
    python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")

from kivy.config import Config
Config.set("graphics", "width",         "600")
Config.set("graphics", "height",        "600")
Config.set("graphics", "minimum_width",  "360")
Config.set("graphics", "minimum_height", "480")
Config.set("graphics", "resizable",    "1")
Config.set("graphics", "borderless",   "0")
Config.set("graphics", "top",          "30")
Config.set("graphics", "left",         "80")
Config.set("input", "mouse", "mouse,multitouch_on_demand")


def _setup_emoji_font():
    from kivy.core.text import LabelBase

    segoe_path = r"C:\Windows\Fonts\seguiemj.ttf"
    if os.path.exists(segoe_path):
        try:
            LabelBase.register(name="NotoEmoji", fn_regular=segoe_path)
            print("[PhytoMed] Emoji font: using Segoe UI Emoji (Windows built-in).")
            return
        except Exception as e:
            print(f"[PhytoMed] Could not register Segoe UI Emoji: {e}")

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    noto_outline = os.path.join(assets_dir, "NotoEmoji-Regular.ttf")
    if os.path.exists(noto_outline):
        try:
            LabelBase.register(name="NotoEmoji", fn_regular=noto_outline)
            print("[PhytoMed] Emoji font: using NotoEmoji-Regular.ttf.")
            return
        except Exception as e:
            print(f"[PhytoMed] Could not register NotoEmoji-Regular: {e}")

    print("[PhytoMed] WARNING: No emoji font found. Emojis will appear as boxes.")


_setup_emoji_font()
print("Hafa Blood")

from ui.app import PhytoMedApp
if __name__ == "__main__":
    print("I dey blood")
    PhytoMedApp().run()
