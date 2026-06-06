"""
ui/screens/home.py
──────────────────
Home screen: animated header, search bar with autocomplete,
recent / quick-access disease chips, and search results list.

Now communicates with the PhytoMed REST API via ApiClient.
"""

import threading
import webbrowser

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import StringProperty

from core.api_client import ApiClient
from ui.theme import *
from ui.widgets import (
    Card, FlatButton, SectionHeader, Chip, Divider,
    BodyLabel, EmptyState, LoadingOverlay
)

WEBSITE_URL = "http://localhost:8000/website/index.html"


# ── Search result row ──────────────────────────────────────────────────────
class ResultRow(Button):
    def __init__(self, item: dict, on_tap, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color  = TRANSPARENT
        self.size_hint_y       = None
        self.height            = dp(72)
        self._item             = item
        self._on_tap           = on_tap

        layout = BoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            padding=[dp(PAD), dp(10), dp(PAD), dp(10)],
            pos=self.pos, size=self.size
        )
        self.bind(pos=lambda *_: setattr(layout, "pos", self.pos),
                  size=lambda *_: setattr(layout, "size", self.size))

        is_disease = item["type"] == "disease"
        badge_bg   = (PRIMARY_LIGHT if is_disease else ACCENT)
        icon_text  = "💊" if is_disease else "🌿"

        badge = BoxLayout(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            orientation="vertical"
        )
        with badge.canvas.before:
            Color(*badge_bg[:3], 0.15)
            RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(12)])
        badge.bind(pos=lambda w, _: badge.canvas.before.clear() or
                   self._redraw_badge(badge, badge_bg),
                   size=lambda w, _: self._redraw_badge(badge, badge_bg))

        icon_lbl = Label(text=icon_text, font_name=FONT_EMOJI, font_size=dp(22))
        badge.add_widget(icon_lbl)

        meta = item["metadata"]
        name = (meta.get("name") or meta.get("english_name") or "Unknown")
        sub  = meta.get("latin_name", "") or meta.get("symptoms", "")[:60]
        if isinstance(sub, list):
            sub = ", ".join(sub[:3])

        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        name_lbl = Label(
            text=name, font_size=dp(FONT_BODY), bold=True,
            color=TEXT_PRIMARY, halign="left", valign="bottom"
        )
        name_lbl.bind(size=name_lbl.setter("text_size"))
        sub_lbl = Label(
            text=sub, font_size=dp(FONT_SM),
            color=TEXT_SECONDARY, halign="left", valign="top"
        )
        sub_lbl.bind(size=sub_lbl.setter("text_size"))
        text_col.add_widget(name_lbl)
        text_col.add_widget(sub_lbl)

        score_txt = f"{item['score']:.0%}" if item["score"] > 0 else ""
        score_lbl = Label(
            text=score_txt,
            font_size=dp(FONT_XS),
            color=TEXT_SECONDARY,
            size_hint=(None, 1),
            width=dp(36),
            halign="right", valign="middle"
        )

        layout.add_widget(badge)
        layout.add_widget(text_col)
        layout.add_widget(score_lbl)
        self.add_widget(layout)

        self.bind(on_press=self._tapped)
        self.bind(pos=self._bg_draw, size=self._bg_draw)

    def _redraw_badge(self, badge, color):
        badge.canvas.before.clear()
        with badge.canvas.before:
            Color(*color[:3], 0.15)
            RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(12)])

    def _bg_draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_CARD)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(0)])

    def _tapped(self, *_):
        anim = Animation(opacity=0.6, d=0.05) + Animation(opacity=1, d=0.1)
        anim.start(self)
        self._on_tap(self._item)


# ── Quick disease chip ─────────────────────────────────────────────────────
class QuickChip(Button):
    def __init__(self, name, disease_id, on_tap, **kwargs):
        super().__init__(**kwargs)
        self.text              = name
        self.background_normal = ""
        self.background_color  = TRANSPARENT
        self.size_hint         = (None, None)
        self.height            = dp(34)
        self.font_size         = dp(FONT_SM)
        self.color             = TEXT_PRIMARY
        self._disease_id       = disease_id
        self._on_tap           = on_tap

        from kivy.core.text import Label as CoreLabel
        cl = CoreLabel(text=name, font_size=dp(FONT_SM))
        cl.refresh()
        self.width = cl.texture.size[0] + dp(24)

        self.bind(pos=self._draw, size=self._draw, on_press=self._tapped)
        self._draw()

    def _draw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*PRIMARY[:3], 0.18)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(17)])

    def _tapped(self, *_):
        self._on_tap(self._disease_id)


# ── Autocomplete dropdown ──────────────────────────────────────────────────
class AutocompleteDropdown(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_y = None
        self.spacing     = dp(1)
        self.opacity     = 0
        self._visible    = False
        with self.canvas.before:
            Color(*BG_INPUT)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[dp(0), dp(0), dp(RADIUS_SM), dp(RADIUS_SM)]
            )
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_INPUT)
            RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[dp(0), dp(0), dp(RADIUS_SM), dp(RADIUS_SM)]
            )

    def show(self, suggestions, on_select):
        self.clear_widgets()
        if not suggestions:
            self.height  = 0
            self.opacity = 0
            return

        for sid, name in suggestions:
            btn = Button(
                text=name,
                font_size=dp(FONT_BODY),
                color=TEXT_PRIMARY,
                halign="left",
                background_normal="",
                background_color=TRANSPARENT,
                size_hint_y=None,
                height=dp(44),
            )
            btn.bind(size=btn.setter("text_size"))
            btn.padding = [dp(PAD), 0]
            _sid = sid
            btn.bind(on_press=lambda b, i=_sid, n=name: on_select(i, n))
            self.add_widget(btn)

        self.height  = dp(44) * len(suggestions)
        self.opacity = 1
        self._visible = True

    def hide(self):
        self.clear_widgets()
        self.height  = 0
        self.opacity = 0
        self._visible = False


# ══════════════════════════════════════════════════════════════════════════
# Home Screen
# ══════════════════════════════════════════════════════════════════════════
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = ApiClient()
        self._search_event = None
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────
    def _build_ui(self):
        root = BoxLayout(orientation="vertical")

        with root.canvas.before:
            Color(*BG_DARK)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *_: setattr(self._bg, "pos",  root.pos),
                  size=lambda *_: setattr(self._bg, "size", root.size))

        root.add_widget(self._build_header())
        root.add_widget(self._build_search_area())

        self._results_scroll = ScrollView(
            size_hint=(1, 1),
            bar_width=dp(3),
            bar_color=PRIMARY_LIGHT,
            bar_inactive_color=BG_DIVIDER,
            do_scroll_x=False,
        )
        self._results_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(2),
        )
        self._results_container.bind(
            minimum_height=self._results_container.setter("height")
        )
        self._results_scroll.add_widget(self._results_container)
        root.add_widget(self._results_scroll)

        self.add_widget(root)
        Clock.schedule_once(self._load_initial, 0.1)

    def _build_header(self):
        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=[dp(PAD), dp(26), dp(PAD), dp(10)],
        )
        with header.canvas.before:
            Color(*PRIMARY_DARK)
            RoundedRectangle(
                pos=header.pos, size=header.size,
                radius=[dp(0), dp(0), dp(24), dp(24)]
            )
        header.bind(
            pos=lambda w, _: self._redraw_header(w),
            size=lambda w, _: self._redraw_header(w)
        )

        # Title row
        title_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        title_lbl = Label(
            text="PhytoMed",
            font_size=dp(FONT_H1),
            bold=True,
            color=WHITE,
            halign="left", valign="middle"
        )
        title_lbl.bind(size=title_lbl.setter("text_size"))

        badge = Label(
            text=" API ",
            font_size=dp(FONT_XS),
            bold=True,
            color=PRIMARY_DARK,
            size_hint=(None, None),
            size=(dp(34), dp(18)),
        )
        with badge.canvas.before:
            Color(*ACCENT)
            RoundedRectangle(pos=badge.pos, size=badge.size, radius=[dp(6)])
        badge.bind(pos=lambda w, _: self._redraw_badge_widget(w),
                   size=lambda w, _: self._redraw_badge_widget(w))

        title_row.add_widget(title_lbl)
        title_row.add_widget(badge)
        title_row.add_widget(Widget())

        subtitle = Label(
            text="Medicinal Plants & Disease Reference",
            font_size=dp(FONT_SM),
            color=(*WHITE[:3], 0.6),
            halign="left", valign="top",
            size_hint_y=None, height=dp(20)
        )
        subtitle.bind(size=subtitle.setter("text_size"))

        # Website button row
        web_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(32),
            spacing=dp(8),
        )
        web_btn = Button(
            text="🌐  Visit Website",
            font_size=dp(FONT_SM),
            bold=True,
            color=WHITE,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint=(None, None),
            size=(dp(150), dp(30)),
        )
        with web_btn.canvas.before:
            Color(*PRIMARY_LIGHT[:3], 0.35)
            RoundedRectangle(pos=web_btn.pos, size=web_btn.size, radius=[dp(15)])
        web_btn.bind(
            pos=lambda w, _: self._redraw_web_btn(w),
            size=lambda w, _: self._redraw_web_btn(w),
            on_press=self._open_website
        )
        web_row.add_widget(web_btn)
        web_row.add_widget(Widget())

        header.add_widget(title_row)
        header.add_widget(subtitle)
        header.add_widget(Widget(size_hint_y=None, height=dp(6)))
        header.add_widget(web_row)

        self._header = header
        return header

    def _redraw_header(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*PRIMARY_DARK)
            RoundedRectangle(
                pos=w.pos, size=w.size,
                radius=[dp(0), dp(0), dp(24), dp(24)]
            )

    def _redraw_badge_widget(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*ACCENT)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(6)])

    def _redraw_web_btn(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*PRIMARY_LIGHT[:3], 0.35)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(15)])

    def _open_website(self, *_):
        webbrowser.open(WEBSITE_URL)

    def _build_search_area(self):
        container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=[dp(PAD), dp(14), dp(PAD), dp(0)],
            spacing=dp(0),
        )
        container.bind(minimum_height=container.setter("height"))

        input_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(8),
        )
        input_wrapper = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            padding=[dp(12), dp(6), dp(12), dp(6)],
        )
        with input_wrapper.canvas.before:
            Color(*BG_INPUT)
            self._input_bg = RoundedRectangle(
                pos=input_wrapper.pos,
                size=input_wrapper.size,
                radius=[dp(RADIUS)]
            )
        input_wrapper.bind(
            pos=lambda w, _: self._redraw_input_bg(w),
            size=lambda w, _: self._redraw_input_bg(w)
        )

        search_icon = Label(
            text="🔍", font_name=FONT_EMOJI, font_size=dp(18),
            size_hint=(None, 1), width=dp(24),
            color=TEXT_SECONDARY
        )

        self._search_input = TextInput(
            hint_text="Search disease, symptom, or plant…",
            font_size=dp(FONT_BODY),
            foreground_color=TEXT_PRIMARY,
            hint_text_color=TEXT_SECONDARY,
            background_color=TRANSPARENT,
            cursor_color=ACCENT,
            multiline=False,
            padding=[0, dp(6)],
        )
        self._search_input.bind(text=self._on_text_changed)

        clear_btn = Button(
            text="✕",
            font_size=dp(14),
            color=TEXT_SECONDARY,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint=(None, 1),
            width=dp(28),
        )
        clear_btn.bind(on_press=self._clear_search)

        input_wrapper.add_widget(search_icon)
        input_wrapper.add_widget(self._search_input)
        input_wrapper.add_widget(clear_btn)
        input_row.add_widget(input_wrapper)
        container.add_widget(input_row)

        self._autocomplete = AutocompleteDropdown()
        container.add_widget(self._autocomplete)

        filter_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(36),
            spacing=dp(8),
            padding=[0, dp(4), 0, dp(0)],
        )
        self._filter_all     = self._make_filter_btn("All", True,     lambda _: self._set_filter(None))
        self._filter_disease = self._make_filter_btn("Diseases", False, lambda _: self._set_filter("disease"))
        self._filter_plant   = self._make_filter_btn("Plants", False,   lambda _: self._set_filter("plant"))
        filter_row.add_widget(self._filter_all)
        filter_row.add_widget(self._filter_disease)
        filter_row.add_widget(self._filter_plant)
        filter_row.add_widget(Widget())
        container.add_widget(filter_row)

        self._active_filter = None
        return container

    def _redraw_input_bg(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*BG_INPUT)
            RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(RADIUS)])

    def _make_filter_btn(self, text, active, callback):
        btn = Button(
            text=text,
            font_size=dp(FONT_SM),
            bold=active,
            color=WHITE if active else TEXT_SECONDARY,
            background_normal="",
            background_color=TRANSPARENT,
            size_hint=(None, 1),
            width=dp(80),
        )
        if active:
            with btn.canvas.before:
                Color(*PRIMARY)
                RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(16)])
            btn.bind(pos=lambda w, _: self._redraw_filter_btn(w, True),
                     size=lambda w, _: self._redraw_filter_btn(w, True))
        btn.bind(on_press=callback)
        return btn

    def _redraw_filter_btn(self, w, active):
        w.canvas.before.clear()
        if active:
            with w.canvas.before:
                Color(*PRIMARY)
                RoundedRectangle(pos=w.pos, size=w.size, radius=[dp(16)])

    def _set_filter(self, filter_type):
        self._active_filter = filter_type
        for btn, ft in [(self._filter_all, None),
                        (self._filter_disease, "disease"),
                        (self._filter_plant, "plant")]:
            active = (ft == filter_type)
            btn.bold  = active
            btn.color = WHITE if active else TEXT_SECONDARY
            self._redraw_filter_btn(btn, active)
        q = self._search_input.text.strip()
        if q:
            self._do_search(q)
        else:
            self._load_initial()

    # ── Events ────────────────────────────────────────────────────────────
    def _on_text_changed(self, instance, text):
        if self._search_event:
            self._search_event.cancel()
        text = text.strip()
        if not text:
            self._autocomplete.hide()
            self._load_initial()
            return
        if self._active_filter != "plant":
            sugg = self.db.autocomplete_diseases(text, 5)
        else:
            rows = self.db.autocomplete_plants(text, 5)
            sugg = [(r[0], r[1]) for r in rows]
        self._autocomplete.show(sugg, self._on_autocomplete_select)
        self._search_event = Clock.schedule_once(
            lambda _: self._do_search(text), 0.4
        )

    def _on_autocomplete_select(self, source_id, name):
        self._autocomplete.hide()
        self._search_input.text = name
        if self._active_filter == "plant":
            self._open_plant(source_id)
        else:
            self._open_disease(source_id)

    def _clear_search(self, *_):
        self._search_input.text = ""
        self._autocomplete.hide()
        self._load_initial()

    # ── Search logic ──────────────────────────────────────────────────────
    def _do_search(self, query):
        def _bg():
            try:
                results = self.db.search(query, top_k=12, doc_type=self._active_filter)
            except Exception as e:
                results = []
                Clock.schedule_once(lambda _: self._show_error(str(e)), 0)
                return
            Clock.schedule_once(lambda _: self._render_results(results), 0)
        threading.Thread(target=_bg, daemon=True).start()

    def _load_initial(self, *_):
        def _bg():
            try:
                diseases = self.db.get_all_diseases()
                plants   = self.db.get_all_plants()
                stats    = self.db.get_stats()
            except Exception as e:
                Clock.schedule_once(lambda _: self._show_error(str(e)), 0)
                return
            Clock.schedule_once(
                lambda _: self._render_browse(diseases, plants, stats), 0
            )
        threading.Thread(target=_bg, daemon=True).start()

    def _show_error(self, msg):
        self._results_container.clear_widgets()
        self._results_container.add_widget(
            EmptyState(
                icon="⚠️",
                title="Cannot reach API server",
                subtitle="Run:  python -m api.server"
            )
        )

    # ── Rendering ─────────────────────────────────────────────────────────
    def _render_results(self, results):
        self._results_container.clear_widgets()
        if not results:
            self._results_container.add_widget(
                EmptyState(
                    icon="🔬",
                    title="No results found",
                    subtitle="Try different keywords or check spelling"
                )
            )
            return
        header = Label(
            text=f"  {len(results)} result(s) found",
            font_size=dp(FONT_SM),
            color=TEXT_SECONDARY,
            halign="left", valign="middle",
            size_hint_y=None, height=dp(30),
        )
        header.bind(size=header.setter("text_size"))
        self._results_container.add_widget(header)
        for item in results:
            row = ResultRow(item, on_tap=self._on_result_tap)
            self._results_container.add_widget(row)
            self._results_container.add_widget(Divider())

    def _render_browse(self, diseases, plants, stats):
        self._results_container.clear_widgets()

        stats_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None, height=dp(56),
            padding=[dp(PAD), dp(6)],
            spacing=dp(16),
        )
        for label, val in [
            ("Diseases", str(stats["diseases"])),
            ("Plants",   str(stats["plants"])),
            ("Remedies", str(stats["links"])),
        ]:
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(
                text=val, font_size=dp(FONT_H2), bold=True,
                color=ACCENT, halign="center"
            ))
            col.add_widget(Label(
                text=label, font_size=dp(FONT_XS),
                color=TEXT_SECONDARY, halign="center"
            ))
            stats_row.add_widget(col)
        self._results_container.add_widget(stats_row)
        self._results_container.add_widget(Divider())

        if self._active_filter != "plant":
            self._results_container.add_widget(self._section_label("Common Diseases"))
            wrap = self._build_chip_row(diseases[:20], self._open_disease)
            self._results_container.add_widget(wrap)
            self._results_container.add_widget(Widget(size_hint_y=None, height=dp(8)))

        if self._active_filter != "disease":
            self._results_container.add_widget(self._section_label("Medicinal Plants"))
            wrap = self._build_chip_row(
                [(p[0], p[1]) for p in plants[:20]],
                self._open_plant
            )
            self._results_container.add_widget(wrap)

        self._results_container.add_widget(Widget(size_hint_y=None, height=dp(20)))

    def _section_label(self, text):
        lbl = Label(
            text=f"  {text}",
            font_size=dp(FONT_H3), bold=True,
            color=TEXT_PRIMARY,
            halign="left", valign="middle",
            size_hint_y=None, height=dp(36),
        )
        lbl.bind(size=lbl.setter("text_size"))
        return lbl

    def _build_chip_row(self, items, on_tap):
        scroll = ScrollView(
            size_hint_y=None, height=dp(44),
            do_scroll_y=False,
            bar_width=0,
        )
        row = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing=dp(8),
            padding=[dp(PAD), dp(5), dp(PAD), dp(5)],
        )
        row.bind(minimum_width=row.setter("width"))
        for sid, name in items:
            chip = QuickChip(name=name, disease_id=sid, on_tap=on_tap)
            row.add_widget(chip)
        scroll.add_widget(row)
        return scroll

    # ── Navigation ────────────────────────────────────────────────────────
    def _on_result_tap(self, item):
        if item["type"] == "disease":
            self._open_disease(item["source_id"])
        else:
            self._open_plant(item["source_id"])

    def _open_disease(self, disease_id):
        app = self.manager.get_screen("disease_detail")
        app.load(disease_id)
        self.manager.transition.direction = "left"
        self.manager.current = "disease_detail"

    def _open_plant(self, plant_id):
        app = self.manager.get_screen("plant_detail")
        app.load(plant_id)
        self.manager.transition.direction = "left"
        self.manager.current = "plant_detail"
