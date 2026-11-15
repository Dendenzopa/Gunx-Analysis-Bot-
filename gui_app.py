
from datetime import date
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Line

from api import APIFootballClient
from basketball_api import BasketballAPIClient


BG = (0.025, 0.04, 0.085, 1)
PANEL = (0.055, 0.085, 0.15, 1)
BLUE = (0.0, 0.55, 1, 1)
GOLD = (1, 0.76, 0.25, 1)
WHITE = (0.94, 0.96, 1, 1)
GREY = (0.62, 0.68, 0.78, 1)
GREEN = (0.2, 0.85, 0.55, 1)


class GunxCard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(12)
        self.spacing = dp(7)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))

        with self.canvas.before:
            Color(*PANEL)
            self.bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *_):
        self.bg.pos = self.pos
        self.bg.size = self.size


class GunxAnalysisApp(App):

    def build(self):
        Window.clearcolor = BG
        self.mode = "FOOTBALL"
        self.api_key = ""
        self.fixtures = []

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        scroll = ScrollView()
        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None
        )
        self.content.bind(
            minimum_height=self.content.setter("height")
        )

        scroll.add_widget(self.content)
        root.add_widget(scroll)

        self.build_header()
        self.build_api_section()
        self.build_navigation()
        self.build_date_section()
        self.build_fixture_section()
        self.build_status()

        return root

    def add_label(self, parent, text, size=14, color=WHITE,
                  bold=False, height=None):
        label = Label(
            text=str(text),
            font_size=sp(size),
            color=color,
            bold=bold,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(height or 30)
        )
        label.bind(size=lambda obj, val: setattr(
            obj, "text_size", (val[0], None)
        ))
        parent.add_widget(label)
        return label

    def build_header(self):
        header = GunxCard(size_hint_y=None)
        header.height = dp(130)

        if __import__("os").path.exists("gunx_logo.png"):
            header.add_widget(Image(
                source="gunx_logo.png",
                size_hint=(1, 0.65),
                allow_stretch=True,
                keep_ratio=True
            ))
        else:
            self.add_label(
                header, "G U N X", 32, GOLD, True, 55
            )

        self.add_label(
            header,
            "THE PULSE OF GLOBAL FOOTBALL ANALYSIS",
            11, BLUE, True, 25
        )
        self.add_label(
            header,
            "FOOTBALL  •  NBA  •  SMART ANALYSIS",
            10, GREY, False, 20
        )
        self.content.add_widget(header)

    def build_api_section(self):
        card = GunxCard()
        self.add_label(card, "API CONNECTION", 16, GOLD, True)

        self.key_input = TextInput(
            hint_text="Enter your API-Sports key",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=(0.08, 0.12, 0.2, 1),
            foreground_color=WHITE,
            hint_text_color=GREY,
            cursor_color=GOLD,
            padding=[dp(10), dp(12)]
        )
        card.add_widget(self.key_input)

        self.content.add_widget(card)

    def build_navigation(self):
        card = GunxCard(size_hint_y=None)
        card.height = dp(100)

        self.add_label(card, "SELECT SPORT", 15, GOLD, True)

        row = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )

        football = Button(
            text="FOOTBALL",
            background_normal="",
            background_color=BLUE,
            color=WHITE,
            bold=True
        )
        nba = Button(
            text="NBA",
            background_normal="",
            background_color=PANEL,
            color=GOLD,
            bold=True
        )

        football.bind(on_release=lambda *_: self.select_mode("FOOTBALL"))
        nba.bind(on_release=lambda *_: self.select_mode("NBA"))

        row.add_widget(football)
        row.add_widget(nba)
        card.add_widget(row)

        self.content.add_widget(card)

    def select_mode(self, mode):
        self.mode = mode
        self.status.text = f"Selected mode: {mode}"
        self.fixture_list.clear_widgets()

    def build_date_section(self):
        card = GunxCard()
        self.add_label(card, "MATCH DATE", 15, GOLD, True)

        self.date_input = TextInput(
            text=date.today().isoformat(),
            hint_text="YYYY-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=(0.08, 0.12, 0.2, 1),
            foreground_color=WHITE,
            cursor_color=GOLD
        )
        card.add_widget(self.date_input)

        load = Button(
            text="LOAD MATCHES",
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=BLUE,
            color=WHITE,
            bold=True
        )
        load.bind(on_release=self.load_matches)
        card.add_widget(load)

        self.content.add_widget(card)

    def build_fixture_section(self):
        self.fixture_card = GunxCard()
        self.add_label(
            self.fixture_card, "MATCH CENTRE", 17, GOLD, True
        )

        self.fixture_list = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )
        self.fixture_list.bind(
            minimum_height=self.fixture_list.setter("height")
        )

        self.fixture_card.add_widget(self.fixture_list)
        self.content.add_widget(self.fixture_card)

    def build_status(self):
        self.status = self.add_label(
            self.content,
            "GUNX SYSTEM READY",
            12, GREEN, True, 35
        )

    def load_matches(self, *_):
        key = self.key_input.text.strip()
        match_date = self.date_input.text.strip()

        if not key:
            self.status.text = "Enter your API key first."
            return

        try:
            date.fromisoformat(match_date)
        except ValueError:
            self.status.text = "Date must use YYYY-MM-DD format."
            return

        self.status.text = "Connecting to API..."
        Thread(
            target=self.fetch_worker,
            args=(key, match_date),
            daemon=True
        ).start()

    def fetch_worker(self, key, match_date):
        try:
            if self.mode == "FOOTBALL":
                client = APIFootballClient(key)
                results = client.get_fixtures(match_date)
            else:
                client = BasketballAPIClient(key)
                results = client.get_games(match_date)

            Clock.schedule_once(
                lambda dt: self.show_matches(results), 0
            )

        except Exception as exc:
            message = str(exc)
            Clock.schedule_once(
                lambda dt: self.show_error(message), 0
            )

    def show_error(self, message):
        self.status.text = "API ERROR: " + message

    def show_matches(self, results):
        self.fixture_list.clear_widgets()
        self.fixtures = results or []

        if not self.fixtures:
            self.add_label(
                self.fixture_list,
                "No matches found for this date.",
                13, GREY
            )
            self.status.text = "No fixtures returned."
            return

        for item in self.fixtures:
            if self.mode == "FOOTBALL":
                home = item.get("home_team", "Home")
                away = item.get("away_team", "Away")
                league = item.get("league", "Football")
                time_text = item.get("date", "")
            else:
                teams = item.get("teams", {})
                home = teams.get("home", {}).get("name", "Home")
                away = teams.get("away", {}).get("name", "Away")
                league = item.get("league", {}).get("name", "Basketball")
                time_text = item.get("date", "")

            card = GunxCard()
            self.add_label(card, f"{home}  VS  {away}",
                           15, WHITE, True)
            self.add_label(card, str(league), 11, GOLD)
            self.add_label(card, str(time_text), 10, GREY)

            self.fixture_list.add_widget(card)

        self.status.text = (
            f"{len(self.fixtures)} matches loaded successfully."
        )


def sp(value):
    return dp(value)


if __name__ == "__main__":
    GunxAnalysisApp().run()
        
