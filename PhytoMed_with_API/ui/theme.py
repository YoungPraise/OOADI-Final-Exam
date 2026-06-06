"""
ui/theme.py
───────────
Centralised design tokens. Edit here to restyle the entire app.
"""

# ── Palette ────────────────────────────────────────────────────────────────
PRIMARY       = (0.071, 0.455, 0.341, 1)    # deep emerald green  #124A57 ish
PRIMARY_DARK  = (0.039, 0.298, 0.220, 1)    # darker shade
PRIMARY_LIGHT = (0.184, 0.600, 0.459, 1)    # lighter accent
ACCENT        = (0.957, 0.714, 0.259, 1)    # warm gold  #F4B642
ACCENT_DARK   = (0.820, 0.569, 0.141, 1)

BG_DARK       = (0.071, 0.082, 0.098, 1)    # near-black bg
BG_CARD       = (0.118, 0.137, 0.165, 1)    # card bg
BG_INPUT      = (0.157, 0.180, 0.212, 1)    # input fields
BG_DIVIDER    = (0.200, 0.220, 0.255, 0.5)

TEXT_PRIMARY  = (0.949, 0.953, 0.957, 1)    # near-white
TEXT_SECONDARY= (0.620, 0.647, 0.698, 1)    # muted
TEXT_ACCENT   = ACCENT
TEXT_DARK     = (0.08,  0.08,  0.08,  1)    # dark text on light bg

SUCCESS       = (0.180, 0.800, 0.443, 1)
WARNING       = (0.957, 0.714, 0.259, 1)
DANGER        = (0.902, 0.329, 0.329, 1)
INFO          = (0.290, 0.565, 0.886, 1)

WHITE         = (1, 1, 1, 1)
BLACK         = (0, 0, 0, 1)
TRANSPARENT   = (0, 0, 0, 0)

# ── Typography ─────────────────────────────────────────────────────────────
FONT_EMOJI = "NotoEmoji"   # registered in main.py; used for all emoji labels
FONT_H1   = 26
FONT_H2   = 20
FONT_H3   = 17
FONT_BODY = 14
FONT_SM   = 12
FONT_XS   = 10

# ── Spacing / radius ───────────────────────────────────────────────────────
RADIUS    = 14
RADIUS_SM = 8
PAD       = 20
PAD_SM    = 12
PAD_XS    = 8

# ── Chip tag colours by category ──────────────────────────────────────────
CHIP_COLORS = {
    "symptom":    (0.290, 0.565, 0.886, 0.20),
    "plant":      (0.180, 0.800, 0.443, 0.18),
    "precaution": (0.957, 0.714, 0.259, 0.20),
    "danger":     (0.902, 0.329, 0.329, 0.22),
}
CHIP_TEXT = {
    "symptom":    INFO,
    "plant":      SUCCESS,
    "precaution": WARNING,
    "danger":     DANGER,
}
