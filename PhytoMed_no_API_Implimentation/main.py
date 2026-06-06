"""
PhytoMed — Medicinal Plants & Disease Reference App
Entry point. Run with: python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")

from kivy.config import Config
Config.set("graphics", "width",        "600")
Config.set("graphics", "height",       "600")
Config.set("graphics", "minimum_width",  "360")
Config.set("graphics", "minimum_height", "480")
Config.set("graphics", "resizable",    "1")
Config.set("graphics", "borderless",   "0")
Config.set("graphics", "top",          "30")
Config.set("graphics", "left",         "80")
Config.set("input", "mouse", "mouse,multitouch_on_demand")


# ── Emoji font setup ───────────────────────────────────────────────────────
def _setup_emoji_font():
    """
    Register an emoji-capable font with Kivy.

    Strategy (in order):
    1. Use Segoe UI Emoji — ships with every Windows 10/11 machine.
       It is a standard outline/vector font that Kivy's FreeType renderer
       handles perfectly. No download required.
    2. Fall back to any NotoEmoji-Regular.ttf already in assets/ (outline,
       not the color-bitmap NotoColorEmoji.ttf which FreeType cannot render).
    3. If nothing is found, warn and continue — emojis will show as boxes
       but the app will still run.
    """
    from kivy.core.text import LabelBase

    # ── Option 1: Segoe UI Emoji (Windows built-in, always present) ──
    segoe_path = r"C:\Windows\Fonts\seguiemj.ttf"
    if os.path.exists(segoe_path):
        try:
            LabelBase.register(name="NotoEmoji", fn_regular=segoe_path)
            print("[PhytoMed] Emoji font: using Segoe UI Emoji (Windows built-in).")
            return
        except Exception as e:
            print(f"[PhytoMed] Could not register Segoe UI Emoji: {e}")

    # ── Option 2: NotoEmoji-Regular.ttf in assets/ (outline version only) ──
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    noto_outline = os.path.join(assets_dir, "NotoEmoji-Regular.ttf")
    if os.path.exists(noto_outline):
        try:
            LabelBase.register(name="NotoEmoji", fn_regular=noto_outline)
            print("[PhytoMed] Emoji font: using NotoEmoji-Regular.ttf.")
            return
        except Exception as e:
            print(f"[PhytoMed] Could not register NotoEmoji-Regular: {e}")

    # ── Option 3: Nothing worked ──
    print("[PhytoMed] WARNING: No emoji font found.")
    print("  Emojis will appear as boxes.")
    print("  To fix: place NotoEmoji-Regular.ttf (NOT NotoColorEmoji) in assets/")
    print("  Download from: https://fonts.google.com/noto/specimen/Noto+Emoji")


_setup_emoji_font()

from ui.app import PhytoMedApp

if __name__ == "__main__":
    PhytoMedApp().run()
