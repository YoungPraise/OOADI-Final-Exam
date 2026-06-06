"""
ui/widgets.py
─────────────
Reusable custom widgets shared across all screens.
"""

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import (
    StringProperty, ColorProperty, NumericProperty,
    BooleanProperty, ListProperty
)
from kivy.animation import Animation

from ui.theme import *


# ── Helpers ────────────────────────────────────────────────────────────────
def rgba(color):
    """Ensure colour is a 4-tuple."""
    if len(color) == 3:
        return (*color, 1)
    return tuple(color)


# ── Rounded card ──────────────────────────────────────────────────────────
class Card(BoxLayout):
    """BoxLayout with rounded corners and card background."""
    bg_color  = ColorProperty(BG_CARD)
    radius    = NumericProperty(RADIUS)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, bg_color=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[dp(self.radius)]
            )


# ── Flat labelled button ───────────────────────────────────────────────────
class FlatButton(Button):
    """Pill-shaped button."""
    bg_color   = ColorProperty(PRIMARY)
    text_color = ColorProperty(WHITE)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal  = ""
        self.background_down    = ""
        self.background_color   = TRANSPARENT
        self.color              = self.text_color
        self.font_size          = dp(FONT_BODY)
        self.bold               = True
        self.size_hint_y        = None
        self.height             = dp(46)
        self.bind(pos=self._redraw, size=self._redraw,
                  bg_color=self._redraw, on_press=self._on_press,
                  on_release=self._on_release)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(RADIUS)])

    def _on_press(self, *_):
        Animation(bg_color=PRIMARY_DARK, d=0.08).start(self)

    def _on_release(self, *_):
        Animation(bg_color=self._orig_color
                  if hasattr(self, "_orig_color") else PRIMARY, d=0.15).start(self)

    def on_bg_color(self, _, color):
        self._orig_color = color


# ── Icon text button ───────────────────────────────────────────────────────
class IconButton(Button):
    """Small circular icon button."""
    bg_color = ColorProperty(BG_INPUT)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color  = TRANSPARENT
        self.size_hint         = (None, None)
        self.size              = (dp(40), dp(40))
        self.color             = TEXT_PRIMARY
        self.font_size         = dp(18)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(20)])


# ── Section header ─────────────────────────────────────────────────────────
class SectionHeader(BoxLayout):
    title      = StringProperty("")
    icon       = StringProperty("")
    icon_color = ColorProperty(ACCENT)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height      = dp(36)
        self.spacing     = dp(8)
        self.padding     = [0, dp(4), 0, dp(4)]
        self._build()
        self.bind(title=self._rebuild, icon=self._rebuild, icon_color=self._rebuild)

    def _build(self):
        self.clear_widgets()
        if self.icon:
            lbl = Label(
                text=self.icon,
                font_name=FONT_EMOJI,
                font_size=dp(16),
                color=self.icon_color,
                size_hint=(None, 1),
                width=dp(24),
                halign="center", valign="middle"
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)
        lbl2 = Label(
            text=self.title,
            font_size=dp(FONT_H3),
            color=TEXT_PRIMARY,
            bold=True,
            halign="left", valign="middle"
        )
        lbl2.bind(size=lbl2.setter("text_size"))
        self.add_widget(lbl2)

        # Accent underline
        line = Widget(size_hint_y=None, height=dp(2))
        with line.canvas:
            Color(*self.icon_color)
            self._line_rect = Rectangle(pos=line.pos, size=line.size)
        line.bind(pos=lambda w, _: setattr(self._line_rect, "pos", w.pos),
                  size=lambda w, _: setattr(self._line_rect, "size", w.size))
        self.add_widget(line)

    def _rebuild(self, *_):
        self._build()


# ── Chip / tag ─────────────────────────────────────────────────────────────
class Chip(BoxLayout):
    """Small pill-shaped tag label."""
    text     = StringProperty("")
    category = StringProperty("symptom")  # symptom | plant | precaution | danger

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint    = (None, None)
        self.height       = dp(28)
        self.padding      = [dp(10), dp(4)]
        self.bind(text=self._build, category=self._build,
                  pos=self._redraw, size=self._redraw)
        self._build()

    def _build(self, *_):
        self.clear_widgets()
        lbl = Label(
            text=self.text,
            font_size=dp(FONT_SM),
            color=CHIP_TEXT.get(self.category, TEXT_PRIMARY),
            size_hint=(None, 1),
        )
        lbl.texture_update()
        lbl.width = lbl.texture_size[0]
        self.width = lbl.width + dp(20)
        self.add_widget(lbl)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*CHIP_COLORS.get(self.category, (0.2, 0.2, 0.2, 0.3)))
            RoundedRectangle(pos=self.pos, size=self.size,
                             radius=[dp(14)])


# ── Chip wrap layout ────────────────────────────────────────────────────────
class ChipWrap(Widget):
    """
    Wraps a list of Chip widgets across multiple rows.
    Dynamic height based on content.
    """
    chips    = ListProperty([])
    category = StringProperty("symptom")
    spacing  = NumericProperty(dp(6))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height      = dp(32)
        self.bind(chips=self._layout, width=self._layout,
                  pos=self._layout)

    def _layout(self, *_):
        self.clear_widgets()
        if not self.chips or self.width <= 0:
            self.height = dp(32)
            return

        x, y    = self.x, self.top
        row_h   = dp(28)
        sp      = self.spacing
        padding = dp(6)
        x       = self.x

        y -= row_h + padding

        for text in self.chips:
            chip = Chip(text=str(text), category=self.category)
            chip.texture_update() if hasattr(chip, "texture_update") else None
            # force layout to compute width
            chip._build()
            w = chip.width

            if x + w > self.right and x > self.x:
                x  = self.x
                y -= row_h + sp

            chip.pos = (x, y)
            self.add_widget(chip)
            x += w + sp

        # Update height
        lowest = min((c.y for c in self.children), default=self.top)
        self.height = max(dp(32), self.top - lowest + row_h + padding)


# ── Divider ────────────────────────────────────────────────────────────────
class Divider(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(1))
        super().__init__(**kwargs)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(*BG_DIVIDER)
            Rectangle(pos=self.pos, size=self.size)


# ── Scrollable body label ──────────────────────────────────────────────────
class BodyLabel(Label):
    """Multi-line body text label, auto-wraps."""
    def __init__(self, **kwargs):
        kwargs.setdefault("font_size",   dp(FONT_BODY))
        kwargs.setdefault("color",       TEXT_SECONDARY)
        kwargs.setdefault("halign",      "left")
        kwargs.setdefault("valign",      "top")
        kwargs.setdefault("size_hint_y", None)
        super().__init__(**kwargs)
        self.bind(width=self._update_text_size, texture_size=self._update_height)

    def _update_text_size(self, *_):
        self.text_size = (self.width, None)

    def _update_height(self, *_):
        self.height = self.texture_size[1]


# ── Info row (label + value) ───────────────────────────────────────────────
class InfoRow(BoxLayout):
    """Horizontal label: value pair."""
    label = StringProperty("")
    value = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height      = dp(32)
        self.spacing     = dp(8)
        self.bind(label=self._build, value=self._build)
        self._build()

    def _build(self, *_):
        self.clear_widgets()
        lbl = Label(
            text=self.label,
            font_size=dp(FONT_SM),
            color=TEXT_SECONDARY,
            size_hint=(None, 1),
            width=dp(110),
            halign="left", valign="middle",
            bold=True
        )
        lbl.bind(size=lbl.setter("text_size"))
        val = Label(
            text=self.value,
            font_size=dp(FONT_SM),
            color=TEXT_PRIMARY,
            halign="left", valign="middle",
        )
        val.bind(size=val.setter("text_size"))
        self.add_widget(lbl)
        self.add_widget(val)


# ── Empty state ────────────────────────────────────────────────────────────
class EmptyState(BoxLayout):
    def __init__(self, icon="🌿", title="No results", subtitle="", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing     = dp(8)
        self.padding     = [dp(PAD), dp(40)]
        self.size_hint_y = None
        self.height      = dp(200)

        self.add_widget(Label(
            text=icon, font_name=FONT_EMOJI, font_size=dp(48),
            size_hint_y=None, height=dp(60),
            color=TEXT_SECONDARY
        ))
        self.add_widget(Label(
            text=title, font_size=dp(FONT_H3),
            bold=True, color=TEXT_PRIMARY,
            size_hint_y=None, height=dp(30)
        ))
        if subtitle:
            lbl = Label(
                text=subtitle, font_size=dp(FONT_BODY),
                color=TEXT_SECONDARY,
                size_hint_y=None, height=dp(40),
                halign="center"
            )
            lbl.bind(size=lbl.setter("text_size"))
            self.add_widget(lbl)


# ── Loading spinner ────────────────────────────────────────────────────────
class LoadingOverlay(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 0.45)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *_: setattr(self._bg, "pos",  self.pos),
                  size=lambda *_: setattr(self._bg, "size", self.size))
        self.add_widget(Label(
            text="Loading…", font_size=dp(18),
            color=WHITE, bold=True,
            pos_hint={"center_x": .5, "center_y": .5}
        ))
