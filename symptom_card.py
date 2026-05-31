"""
SymptomCard Widget
------------------
A reusable card widget that displays a single plant symptom in a
readable, styled format. Used on the symptom-results screen.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import StringProperty, StringProperty, ListProperty
from kivy.metrics import dp
from kivy.lang import Builder

Builder.load_string("""
<SymptomCard>:
    orientation: 'vertical'
    padding: dp(14), dp(12)
    spacing: dp(6)
    size_hint_y: None
    height: self.minimum_height

    canvas.before:
        Color:
            rgba: root.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
        Color:
            rgba: root.border_color
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(12))
            width: 1.4

    # Severity badge row
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(28)
        spacing: dp(8)

        # Severity dot
        Widget:
            size_hint: None, None
            size: dp(10), dp(10)
            pos_hint: {'center_y': 0.5}
            canvas:
                Color:
                    rgba: root.severity_color
                Ellipse:
                    pos: self.pos
                    size: self.size

        Label:
            text: root.severity_label
            font_size: sp(11)
            bold: True
            color: root.severity_color
            size_hint_x: None
            width: self.texture_size[0]
            halign: 'left'

        Widget:  # spacer
            size_hint_x: 1

        Label:
            text: root.category
            font_size: sp(11)
            color: 0.5, 0.55, 0.5, 1
            size_hint_x: None
            width: self.texture_size[0]
            halign: 'right'

    # Symptom name
    Label:
        text: root.symptom_name
        font_size: sp(15)
        bold: True
        color: root.title_color
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        halign: 'left'
        valign: 'top'

    # Description
    Label:
        text: root.description
        font_size: sp(13)
        color: root.body_color
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        halign: 'left'
        valign: 'top'
""")


# Severity level constants
SEVERITY_HIGH   = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW    = "low"

_SEVERITY_META = {
    SEVERITY_HIGH:   {"label": "⚠ HIGH",   "color": (0.85, 0.25, 0.20, 1)},
    SEVERITY_MEDIUM: {"label": "● MEDIUM", "color": (0.88, 0.60, 0.10, 1)},
    SEVERITY_LOW:    {"label": "✓ LOW",    "color": (0.25, 0.62, 0.35, 1)},
}


class SymptomCard(BoxLayout):
    """
    Displays one symptom entry.

    Parameters
    ----------
    symptom_name : str
        Short name / title of the symptom (e.g. "Yellowing Leaves").
    description  : str
        One-to-three sentence explanation shown below the title.
    severity     : str
        One of ``"high"``, ``"medium"``, or ``"low"``.  Controls the
        colour-coded badge and left-border accent.
    category     : str, optional
        Optional tag shown top-right (e.g. "Nutrient", "Pest", "Water").
    """

    symptom_name   = StringProperty("Symptom")
    description    = StringProperty("")
    severity       = StringProperty(SEVERITY_LOW)
    category       = StringProperty("")

    # Derived display properties (auto-updated via on_severity)
    severity_label = StringProperty("✓ LOW")
    severity_color = ListProperty([0.25, 0.62, 0.35, 1])

    # Theme colours  — greens / earth tones
    card_color   = ListProperty([0.95, 0.97, 0.94, 1])
    border_color = ListProperty([0.78, 0.88, 0.76, 0.8])
    title_color  = ListProperty([0.13, 0.27, 0.14, 1])
    body_color   = ListProperty([0.25, 0.32, 0.25, 1])

    # ------------------------------------------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(severity=self._apply_severity)
        self._apply_severity()

    # ------------------------------------------------------------------
    def _apply_severity(self, *_):
        meta = _SEVERITY_META.get(self.severity, _SEVERITY_META[SEVERITY_LOW])
        self.severity_label = meta["label"]
        self.severity_color = list(meta["color"])

        # Tint the card background slightly for HIGH severity
        if self.severity == SEVERITY_HIGH:
            self.card_color   = [0.99, 0.95, 0.94, 1]
            self.border_color = [0.90, 0.70, 0.68, 0.9]
        elif self.severity == SEVERITY_MEDIUM:
            self.card_color   = [0.99, 0.97, 0.92, 1]
            self.border_color = [0.92, 0.82, 0.60, 0.9]
        else:
            self.card_color   = [0.95, 0.97, 0.94, 1]
            self.border_color = [0.78, 0.88, 0.76, 0.8]
