"""
ui/screens/plant_detail.py
───────────────────────────
Full-detail screen for a single medicinal plant.
Now fetches data from the REST API via ApiClient.
"""

import threading

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock

from core.api_client import ApiClient
from ui.theme import *
from ui.widgets import (
    SectionHeader, Divider, BodyLabel,
    EmptyState, LoadingOverlay, Chip
)


# ── Disease treat row ──────────────────────────────────────────────────────
class TreatsRow(BoxLayout):
    def __init__(self, disease_data: dict, on_tap, **kwargs):
        super().__init__(**kwargs)
        self.orientation   = "horizontal"
        self.size_hint_y   = None
        self.height        = dp(68)
        self.spacing       = dp(10)
        self.padding       = [dp(PAD), dp(8), dp(PAD), dp(8)]
        self._disease_data = disease_data
        self._on_tap       = on_tap
        self.bind(pos=self._bg, size=self._bg)
        self._build()

    def _bg(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_CARD)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(RADIUS_SM)])

    def _build(self):
        d = self._disease_data

        icon = Label(
            text="💊",
            font_name=FONT_EMOJI,
            font_size=dp(20),
            size_hint=(None, 1),
            width=dp(32)
        )

        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        name_lbl = Label(
            text=d.get("name", ""),
            font_size=dp(FONT_BODY), bold=True,
            color=TEXT_PRIMARY,
            halign="left", valign="bottom"
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))

        part     = d.get("part_of_plant", "")
        prep_raw = d.get("preparation_method", "")
        sub_text = f"{part} · {prep_raw[:55]}…" if len(prep_raw) > 55 else f"{part} · {prep_raw}"
        sub_lbl  = Label(
            text=sub_text,
            font_size=dp(FONT_XS),
            color=TEXT_SECONDARY,
            halign="left", valign="top"
        )
        sub_lbl.bind(size=sub_lbl.setter("text_size"))

        text_col.add_widget(name_lbl)
        text_col.add_widget(sub_lbl)

        view_btn = Button(
            text="View",
            font_size=dp(FONT_SM),
            bold=True,
            color=WHITE,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint=(None, None),
            size=(dp(60), dp(34)),
            pos_hint={"center_y": 0.5},
        )
        view_btn.bind(
            pos=lambda w, _: self._redraw_btn(w),
            size=lambda w, _: self._redraw_btn(w),
            on_press=lambda _: self._on_tap(self._disease_data["id"])
        )

        self.add_widget(icon)
        self.add_widget(text_col)
        self.add_widget(view_btn)

    def _redraw_btn(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*PRIMARY)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(8)])


# ══════════════════════════════════════════════════════════════════════════
# Plant Detail Screen
# ══════════════════════════════════════════════════════════════════════════
class PlantDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = ApiClient()
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
            font_size=dp(FONT_BODY), bold=True,
            color=WHITE,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint=(None, 1),
            width=dp(80),
        )
        back_btn.bind(on_press=self._go_back)

        self._title_lbl = Label(
            text="Plant",
            font_size=dp(FONT_H3), bold=True,
            color=WHITE,
            halign="center", valign="middle"
        )
        self._title_lbl.bind(size=self._title_lbl.setter("text_size"))

        bar.add_widget(back_btn)
        bar.add_widget(self._title_lbl)
        bar.add_widget(Widget(size_hint=(None, 1), width=dp(80)))
        return bar

    # ── Public ────────────────────────────────────────────────────────────
    def load(self, plant_id: int):
        self._content.clear_widgets()
        self._content.add_widget(LoadingOverlay(size_hint=(1, None), height=dp(200)))
        threading.Thread(target=self._fetch, args=(plant_id,), daemon=True).start()

    def _fetch(self, plant_id):
        try:
            data = self.db.get_plant(plant_id)
        except Exception:
            data = None
        Clock.schedule_once(lambda _: self._render(data), 0)

    # ── Render ────────────────────────────────────────────────────────────
    def _render(self, data):
        self._content.clear_widgets()
        if not data:
            self._content.add_widget(EmptyState(title="Plant not found"))
            return

        en_name = data.get("english_name") or data.get("latin_name") or "Plant"
        self._title_lbl.text = en_name

        # Hero card
        hero = BoxLayout(orientation="vertical", size_hint_y=None, padding=[dp(20), dp(18)], spacing=dp(8))
        hero.bind(minimum_height=hero.setter("height"))
        with hero.canvas.before:
            Color(*PRIMARY_DARK)
            RoundedRectangle(pos=hero.pos, size=hero.size, radius=[dp(RADIUS)])
        hero.bind(pos=lambda w, _: self._redraw_card(w),
                  size=lambda w, _: self._redraw_card(w))

        name_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(42), spacing=dp(10))
        icon_lbl = Label(text="🌿", font_name=FONT_EMOJI, font_size=dp(30), size_hint=(None, 1), width=dp(40))
        name_col = BoxLayout(orientation="vertical", spacing=dp(2))
        n_lbl = Label(text=en_name, font_size=dp(FONT_H2), bold=True, color=WHITE, halign="left", valign="bottom")
        n_lbl.bind(size=n_lbl.setter("text_size"))
        lat_lbl = Label(
            text=data.get("latin_name", ""),
            font_size=dp(FONT_SM), color=(*WHITE[:3], 0.6),
            halign="left", valign="top", italic=True
        )
        lat_lbl.bind(size=lat_lbl.setter("text_size"))
        name_col.add_widget(n_lbl)
        name_col.add_widget(lat_lbl)
        name_row.add_widget(icon_lbl)
        name_row.add_widget(name_col)
        hero.add_widget(name_row)

        treats = data.get("treats", [])
        badge = Label(
            text=f"💊 Treats {len(treats)} disease{'s' if len(treats) != 1 else ''}",
            font_name=FONT_EMOJI, font_size=dp(FONT_SM),
            color=(*ACCENT[:3], 0.9),
            halign="left", valign="middle",
            size_hint_y=None, height=dp(22),
        )
        badge.bind(size=badge.setter("text_size"))
        hero.add_widget(badge)
        self._content.add_widget(hero)

        desc = data.get("description", "")
        if desc:
            self._content.add_widget(SectionHeader(title="Description", icon="📖"))
            self._content.add_widget(BodyLabel(text=desc))

        loc = data.get("location", "")
        cam = data.get("cameroon_location", "")
        if loc or cam:
            self._content.add_widget(SectionHeader(title="Geographic Location", icon="📍", icon_color=INFO))
            if loc:
                self._content.add_widget(BodyLabel(text=loc))
            if cam:
                cam_lbl = Label(
                    text="📍 In Cameroon:", font_name=FONT_EMOJI,
                    font_size=dp(FONT_SM), bold=True, color=INFO,
                    halign="left", valign="middle", size_hint_y=None, height=dp(24),
                )
                cam_lbl.bind(size=cam_lbl.setter("text_size"))
                self._content.add_widget(cam_lbl)
                self._content.add_widget(BodyLabel(text=cam))

        med = data.get("medicinal_use", "")
        if med:
            self._content.add_widget(SectionHeader(title="Medicinal Use", icon="💊", icon_color=SUCCESS))
            self._content.add_widget(BodyLabel(text=med, color=TEXT_PRIMARY))

        steps = data.get("application_steps", "")
        if steps:
            self._content.add_widget(SectionHeader(title="How to Use", icon="📋", icon_color=PRIMARY_LIGHT))
            self._content.add_widget(BodyLabel(text=steps))

        prec = data.get("precautions", "")
        if prec:
            self._content.add_widget(SectionHeader(title="Precautions", icon="⚠️", icon_color=WARNING))
            self._content.add_widget(BodyLabel(text=prec, color=WARNING))

        tox = data.get("toxicity", "")
        if tox:
            self._content.add_widget(SectionHeader(title="Toxicity", icon="☠️", icon_color=DANGER))
            self._content.add_widget(BodyLabel(text=tox, color=DANGER))

        if treats:
            self._content.add_widget(
                SectionHeader(title=f"Diseases Treated ({len(treats)})", icon="💊", icon_color=INFO)
            )
            for disease in treats:
                row = TreatsRow(disease_data=disease, on_tap=self._open_disease, size_hint_y=None, height=dp(60))
                self._content.add_widget(row)
                self._content.add_widget(Divider())

        self._content.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def _redraw_card(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*PRIMARY_DARK)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(RADIUS)])

    def _go_back(self, *_):
        self.manager.transition.direction = "right"
        self.manager.current = self.manager.previous()

    def _open_disease(self, disease_id):
        screen = self.manager.get_screen("disease_detail")
        screen.load(disease_id)
        self.manager.transition.direction = "left"
        self.manager.current = "disease_detail"
