"""
ui/screens/disease_detail.py
─────────────────────────────
Full-detail screen for a single disease.
Now fetches data from the REST API via ApiClient.
"""

import threading

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation

from core.api_client import ApiClient
from ui.theme import *
from ui.widgets import (
    Card, FlatButton, SectionHeader, Chip, Divider,
    BodyLabel, EmptyState, LoadingOverlay, ChipWrap
)


# ── Plant remedy card ──────────────────────────────────────────────────────
class PlantRemedyCard(BoxLayout):
    """Expandable card showing one plant's remedy for this disease."""

    def __init__(self, plant_data: dict, on_view_plant, **kwargs):
        super().__init__(**kwargs)
        self.orientation  = "vertical"
        self.size_hint_y  = None
        self.spacing      = dp(0)
        self.padding      = [dp(16), dp(14), dp(16), dp(14)]
        self._expanded    = False
        self._plant_data  = plant_data
        self._on_view     = on_view_plant
        self._build()
        self.bind(pos=self._redraw, size=self._redraw)
        self._update_height()

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_CARD)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(RADIUS)])

    def _build(self):
        p = self._plant_data

        header_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(52),
            spacing=dp(10)
        )

        icon_box = BoxLayout(size_hint=(None, None), size=(dp(40), dp(40)))
        icon_box.bind(pos=lambda w, _: self._redraw_icon(w),
                      size=lambda w, _: self._redraw_icon(w))
        icon_lbl = Label(text="🌿", font_name=FONT_EMOJI, font_size=dp(20))
        icon_box.add_widget(icon_lbl)

        names_col = BoxLayout(orientation="vertical", spacing=dp(2))
        en_name   = p.get("english_name") or p.get("latin_name") or "Unknown Plant"
        la_name   = p.get("latin_name", "")
        name_lbl  = Label(
            text=en_name,
            font_size=dp(FONT_BODY), bold=True,
            color=TEXT_PRIMARY,
            halign="left", valign="bottom"
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))
        latin_lbl = Label(
            text=la_name,
            font_size=dp(FONT_XS),
            color=TEXT_SECONDARY,
            halign="left", valign="top"
        )
        latin_lbl.bind(size=latin_lbl.setter("text_size"))
        names_col.add_widget(name_lbl)
        names_col.add_widget(latin_lbl)

        part     = p.get("part_of_plant", "")
        part_lbl = Label(
            text=part,
            font_size=dp(FONT_XS),
            color=ACCENT,
            size_hint=(None, None),
            size=(dp(80), dp(20)),
            halign="right", valign="middle",
            bold=True
        )
        part_lbl.bind(size=part_lbl.setter("text_size"))

        self._toggle_btn = Button(
            text="▼",
            font_size=dp(12),
            color=TEXT_SECONDARY,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint=(None, 1),
            width=dp(28),
        )
        self._toggle_btn.bind(on_press=self._toggle_expand)

        header_row.add_widget(icon_box)
        header_row.add_widget(names_col)
        header_row.add_widget(part_lbl)
        header_row.add_widget(self._toggle_btn)
        self.add_widget(header_row)

        prep = p.get("preparation_method", "")
        preview = (prep[:100] + "…") if len(prep) > 100 else prep
        self._preview_lbl = Label(
            text=preview,
            font_size=dp(FONT_SM),
            color=TEXT_SECONDARY,
            halign="left", valign="top",
            size_hint_y=None, height=dp(36)
        )
        self._preview_lbl.bind(size=self._preview_lbl.setter("text_size"))
        self.add_widget(self._preview_lbl)

        self._expand_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10),
            height=0,
            opacity=0,
        )
        self._build_expanded_content(self._expand_box, p)
        self.add_widget(self._expand_box)

    def _redraw_icon(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*PRIMARY_LIGHT[:3], 0.25)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(20)])
        for child in w.children:
            child.pos  = w.pos
            child.size = w.size

    def _build_expanded_content(self, box, p):
        box.clear_widgets()
        div = Divider()
        div.size_hint_y = None
        div.height      = dp(1)
        box.add_widget(div)

        prep = p.get("preparation_method", "")
        if prep:
            box.add_widget(self._exp_section("📋 Preparation", prep))

        med = p.get("medicinal_use", "")
        if med:
            box.add_widget(self._exp_section("💊 Medicinal Use", med[:400]))

        prec = p.get("precautions", "")
        if prec:
            box.add_widget(self._exp_section("⚠️ Precautions", prec[:300], color=WARNING))

        view_btn = Button(
            text="View Full Plant Profile  →",
            font_size=dp(FONT_SM),
            bold=True,
            color=PRIMARY_LIGHT,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint_y=None, height=dp(36),
            halign="right",
        )
        _pid = p.get("id")
        view_btn.bind(on_press=lambda _: self._on_view(_pid))
        box.add_widget(view_btn)

    def _exp_section(self, title, text, color=TEXT_SECONDARY):
        col = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4))
        title_lbl = Label(
            text=title,
            font_name=FONT_EMOJI,
            font_size=dp(FONT_SM), bold=True,
            color=TEXT_PRIMARY,
            halign="left", valign="middle",
            size_hint_y=None, height=dp(22),
        )
        title_lbl.bind(size=title_lbl.setter("text_size"))
        body_lbl = BodyLabel(text=text, color=color)
        col.add_widget(title_lbl)
        col.add_widget(body_lbl)
        col.bind(minimum_height=col.setter("height"))
        return col

    def _toggle_expand(self, *_):
        self._expanded = not self._expanded
        if self._expanded:
            self._toggle_btn.text = "▲"
            self._preview_lbl.opacity = 0
            self._preview_lbl.height  = 0
            self._expand_box.opacity = 1
            self._expand_box.height = None
            self._expand_box.size_hint_y = None
            Clock.schedule_once(self._set_expanded_height, 0.05)
        else:
            self._toggle_btn.text = "▼"
            self._preview_lbl.opacity = 1
            self._preview_lbl.height  = dp(36)
            self._expand_box.height   = 0
            self._expand_box.opacity  = 0
            self._update_height()

    def _set_expanded_height(self, *_):
        total = 0
        for child in self._expand_box.children:
            total += child.height + self._expand_box.spacing
        self._expand_box.height = total + dp(10)
        self._update_height()

    def _update_height(self, *_):
        total = dp(52)
        if self._expanded:
            total += self._expand_box.height + dp(10)
        else:
            total += dp(36) + dp(10)
        total += dp(28)
        self.height = total


# ══════════════════════════════════════════════════════════════════════════
# Disease Detail Screen
# ══════════════════════════════════════════════════════════════════════════
class DiseaseDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = ApiClient()
        self._disease_id = None
        self._build_skeleton()

    def _build_skeleton(self):
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*BG_DARK)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *_: setattr(self._bg, "pos",  root.pos),
                  size=lambda *_: setattr(self._bg, "size", root.size))

        root.add_widget(self._build_topbar())

        self._scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(3),
            bar_color=PRIMARY_LIGHT,
            do_scroll_x=False,
        )
        self._content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(PAD), dp(10), dp(PAD), dp(30)],
            spacing=dp(16),
        )
        self._content.bind(minimum_height=self._content.setter("height"))
        self._scroll.add_widget(self._content)
        root.add_widget(self._scroll)
        self.add_widget(root)

    def _build_topbar(self):
        bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(56),
            padding=[dp(PAD_SM), dp(8)],
            spacing=dp(8),
        )
        with bar.canvas.before:
            Color(*PRIMARY_DARK)
            self._bar_bg = Rectangle(pos=bar.pos, size=bar.size)
        bar.bind(pos=lambda *_: setattr(self._bar_bg, "pos",  bar.pos),
                 size=lambda *_: setattr(self._bar_bg, "size", bar.size))

        back_btn = Button(
            text="< Back",
            font_size=dp(FONT_BODY),
            color=WHITE,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint=(None, 1),
            width=dp(80),
            halign="left",
            bold=True,
        )
        back_btn.bind(on_press=self._go_back)

        self._title_lbl = Label(
            text="Disease",
            font_size=dp(FONT_H3),
            bold=True, color=WHITE,
            halign="center", valign="middle"
        )
        self._title_lbl.bind(size=self._title_lbl.setter("text_size"))

        bar.add_widget(back_btn)
        bar.add_widget(self._title_lbl)
        bar.add_widget(Widget(size_hint=(None, 1), width=dp(80)))
        return bar

    # ── Public ────────────────────────────────────────────────────────────
    def load(self, disease_id: int):
        self._disease_id = disease_id
        self._content.clear_widgets()
        self._content.add_widget(LoadingOverlay(size_hint=(1, None), height=dp(200)))
        threading.Thread(target=self._fetch, args=(disease_id,), daemon=True).start()

    def _fetch(self, disease_id):
        try:
            data = self.db.get_disease(disease_id)
        except Exception:
            data = None
        Clock.schedule_once(lambda _: self._render(data), 0)

    # ── Render ────────────────────────────────────────────────────────────
    def _render(self, data):
        self._content.clear_widgets()
        if not data:
            self._content.add_widget(EmptyState(title="Disease not found"))
            return

        self._title_lbl.text = data["name"]

        # Hero card
        hero = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(20), dp(18)],
            spacing=dp(10),
        )
        with hero.canvas.before:
            Color(*PRIMARY_DARK)
            RoundedRectangle(pos=hero.pos, size=hero.size, radius=[dp(RADIUS)])
        hero.bind(pos=lambda w, _: self._redraw_card(w, PRIMARY_DARK),
                  size=lambda w, _: self._redraw_card(w, PRIMARY_DARK),
                  minimum_height=hero.setter("height"))

        name_lbl = Label(
            text=data["name"],
            font_size=dp(FONT_H1), bold=True,
            color=WHITE,
            halign="left", valign="middle",
            size_hint_y=None, height=dp(38),
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))
        hero.add_widget(name_lbl)

        pc = len(data.get("plants", []))
        badge_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24), spacing=dp(8))
        badge_lbl = Label(
            text=f"🌿 {pc} medicinal plant{'s' if pc!=1 else ''} available",
            font_name=FONT_EMOJI,
            font_size=dp(FONT_SM),
            color=(*ACCENT[:3], 0.9),
            halign="left", valign="middle",
            size_hint_y=None, height=dp(24),
        )
        badge_lbl.bind(size=badge_lbl.setter("text_size"))
        badge_row.add_widget(badge_lbl)
        badge_row.add_widget(Widget())
        hero.add_widget(badge_row)
        self._content.add_widget(hero)

        if data.get("description"):
            self._content.add_widget(SectionHeader(title="About", icon="📖"))
            self._content.add_widget(BodyLabel(text=data["description"]))

        syms = data.get("symptoms", [])
        if syms:
            self._content.add_widget(SectionHeader(title="Symptoms", icon="🩺"))
            chips_col = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
            chips_col.bind(minimum_height=chips_col.setter("height"))
            row = None
            row_width = 0
            max_width = 320
            for sym in syms:
                chip = Chip(text=sym.capitalize(), category="symptom")
                chip._build()
                cw = chip.width
                if row is None or row_width + cw + dp(6) > dp(max_width):
                    row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32), spacing=dp(6))
                    chips_col.add_widget(row)
                    row_width = 0
                row.add_widget(chip)
                row.add_widget(Widget(size_hint_x=None, width=dp(0)))
                row_width += cw + dp(6)
            if row:
                row.add_widget(Widget())
            self._content.add_widget(chips_col)

        if data.get("prevention"):
            self._content.add_widget(SectionHeader(title="Prevention", icon="🛡️"))
            self._content.add_widget(BodyLabel(text=data["prevention"]))

        plants = data.get("plants", [])
        if plants:
            self._content.add_widget(
                SectionHeader(title=f"Medicinal Remedies ({len(plants)})", icon="🌿", icon_color=SUCCESS)
            )
            info_lbl = Label(
                text="Tap a card to expand preparation details",
                font_size=dp(FONT_XS),
                color=TEXT_SECONDARY,
                halign="left", valign="middle",
                size_hint_y=None, height=dp(20),
            )
            info_lbl.bind(size=info_lbl.setter("text_size"))
            self._content.add_widget(info_lbl)
            for plant in plants:
                card = PlantRemedyCard(plant_data=plant, on_view_plant=self._open_plant)
                self._content.add_widget(card)
        else:
            self._content.add_widget(
                EmptyState(icon="🔎", title="No plant remedies recorded",
                           subtitle="No traditional plant remedies linked to this disease yet.")
            )

        self._content.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def _redraw_card(self, w, color):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*color)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(RADIUS)])

    def _go_back(self, *_):
        self.manager.transition.direction = "right"
        self.manager.current = "home"

    def _open_plant(self, plant_id):
        if plant_id is None:
            return
        screen = self.manager.get_screen("plant_detail")
        screen.load(plant_id)
        self.manager.transition.direction = "left"
        self.manager.current = "plant_detail"
