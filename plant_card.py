"""
PlantCard Widget
----------------
A tappable summary card that shows a plant's name, short description,
and thumbnail image.  Tapping the card navigates to the full plant
detail screen via an on_press callback.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.lang import Builder

Builder.load_string("""
<PlantCard>:
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(12)
    size_hint_y: None
    height: dp(90)

    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        Color:
            rgba: root.border_color
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, dp(14))
            width: 1.2

    # Thumbnail
    AsyncImage:
        id: thumb
        source: root.image_source
        size_hint: None, None
        size: dp(68), dp(68)
        pos_hint: {'center_y': 0.5}
        allow_stretch: True
        keep_ratio: True
        # Rounded clip via canvas
        canvas.before:
            StencilPush
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(10)]
            StencilUse
        canvas.after:
            StencilUnUse
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(10)]
            StencilPop

    # Text column
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(4)
        padding: 0, dp(6), dp(4), dp(6)

        Label:
            text: root.plant_name
            font_size: sp(15)
            bold: True
            color: root.title_color
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            halign: 'left'
            valign: 'middle'

        Label:
            text: root.short_description
            font_size: sp(12)
            color: root.body_color
            size_hint_y: 1
            text_size: self.width, None
            halign: 'left'
            valign: 'top'

    # Chevron
    Label:
        text: '›'
        font_size: sp(24)
        color: root.accent_color
        size_hint: None, 1
        width: dp(20)
        halign: 'center'
        valign: 'middle'
""")


class PlantCard(ButtonBehavior, BoxLayout):
    """
    Tappable summary card for one plant entry.

    Parameters
    ----------
    plant_name        : str  — Common name of the plant.
    short_description : str  — One-sentence summary (≤ 120 chars recommended).
    image_source      : str  — Path or URL for the thumbnail image.
                               Falls back to the bundled placeholder.
    on_press          : callable (optional)
                        Kivy ButtonBehavior ``on_press`` event.  Bind it to
                        navigate to the plant detail screen, e.g.::

                            card = PlantCard(plant_name="Basil", ...)
                            card.bind(on_press=lambda *_: app.show_plant(card.plant_name))
    """

    plant_name        = StringProperty("Plant Name")
    short_description = StringProperty("Tap to learn more about this plant.")
    image_source      = StringProperty("assets/images/placeholder.png")

    # Theme colours — earthy greens
    bg_color     = ListProperty([0.96, 0.98, 0.95, 1])
    border_color = ListProperty([0.76, 0.87, 0.74, 0.85])
    title_color  = ListProperty([0.12, 0.26, 0.13, 1])
    body_color   = ListProperty([0.28, 0.36, 0.27, 1])
    accent_color = ListProperty([0.22, 0.55, 0.30, 1])

    # ------------------------------------------------------------------
    def on_press(self):
        """Animate a subtle press-down effect."""
        anim = Animation(
            opacity=0.82,
            duration=0.08,
        )
        anim.start(self)

    def on_release(self):
        anim = Animation(opacity=1.0, duration=0.12)
        anim.start(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._scale_down()
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self._scale_up()
        return super().on_touch_up(touch)

    # ------------------------------------------------------------------
    def _scale_down(self):
        Animation(
            padding=[dp(10), dp(10), dp(10), dp(10)],  # slight indent
            duration=0.07,
        ).start(self)

    def _scale_up(self):
        Animation(
            padding=[dp(10), dp(10), dp(10), dp(10)],
            duration=0.12,
        ).start(self)
