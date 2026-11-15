
from datetime import date
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle

from api import APIFootballClient
from basketball_api import BasketballAPIClient
from football_engine import GunxFootballEngine


# GUNX COLOURS
BG = (0.025, 0.035, 0.075, 1)
CARD = (0.055, 0.075, 0.13, 1)
BLUE = (0.05, 0.42, 0.95, 1)
GOLD = (0.95, 0.70, 0.18, 1)
WHITE = (0.94, 0.96, 1, 1)
GREY = (0.62, 0.68, 0.78, 1)
GREEN = (0.15, 0.75, 0.43, 1)
RED = (0.85, 0.25, 0.25, 1)


class GunxCard(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = dp(12)
        self.spacing = dp(8)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter("height"))

        with self.canvas.before:
            Color(*CARD)
            self.bg_rect = RoundedRectangle(
                radius=[dp(12)]
            )

        self.bind(
            pos=self.update_bg,
            size=self.update_bg
        )

    def update_bg(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class GunxAnalysisApp(App):

    def build(self):
        Window.clearcolor = BG

        self.mode = "FOOTBALL"
        self.api_key = ""
        self.fixtures = []
        self.fixture_container = None
        self.status_label = None
        self.analysis_area = None

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        root.add_widget(self.build_header())
        root.add_widget(self.build_api_section())
        root.add_widget(self.build_navigation())
        root.add_widget(self.build_date_section())

        self.status_label = Label(
            text="GUNX READY",
            color=GREEN,
            size_hint_y=None,
            height=dp(30),
            font_size="12sp"
        )
        root.add_widget(self.status_label)

        scroll = ScrollView(
            do_scroll_x=False
        )

        self.fixture_container = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=(0, dp(5))
        )
        self.fixture_container.bind(
            minimum_height=self.fixture_container.setter("height")
        )

        scroll.add_widget(self.fixture_container)
        root.add_widget(scroll)

        return root

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    def build_header(self):

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(105),
            spacing=dp(3)
        )

        try:
            logo = Image(
                source="gunx_logo.png",
                size_hint=(1, None),
                height=dp(65),
                fit_mode="contain"
            )
            header.add_widget(logo)

        except Exception:
            title = Label(
                text="[b]GUNX[/b] [color=3399FF]ANALYSIS BOT[/color]",
                markup=True,
                font_size="25sp",
                color=GOLD,
                size_hint_y=None,
                height=dp(55)
            )
            header.add_widget(title)

        subtitle = Label(
            text="THE PULSE OF GLOBAL FOOTBALL ANALYSIS",
            color=GREY,
            font_size="10sp",
            size_hint_y=None,
            height=dp(25)
        )
        header.add_widget(subtitle)

        return header

    # --------------------------------------------------
    # API KEY
    # --------------------------------------------------

    def build_api_section(self):

        card = GunxCard(
            size_hint_y=None,
            spacing=dp(7)
        )

        card.add_widget(Label(
            text="[b]API CONNECTION[/b]",
            markup=True,
            color=GOLD,
            size_hint_y=None,
            height=dp(25)
        ))

        self.api_key_input = TextInput(
            hint_text="Enter your API-Sports key",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            foreground_color=WHITE,
            hint_text_color=GREY,
            background_color=(0.08, 0.10, 0.17, 1),
            cursor_color=GOLD
        )

        card.add_widget(self.api_key_input)

        return card

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------

    def build_navigation(self):

        nav = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )

        football_button = Button(
            text="FOOTBALL",
            background_normal="",
            background_color=BLUE,
            color=WHITE
        )

        basketball_button = Button(
            text="NBA",
            background_normal="",
            background_color=CARD,
            color=GOLD
        )

        football_button.bind(
            on_release=lambda *_: self.change_mode("FOOTBALL")
        )

        basketball_button.bind(
            on_release=lambda *_: self.change_mode("NBA")
        )

        nav.add_widget(football_button)
        nav.add_widget(basketball_button)

        return nav

    def change_mode(self, mode):

        self.mode = mode
        self.fixture_container.clear_widgets()

        if mode == "FOOTBALL":
            self.set_status(
                "FOOTBALL MODE SELECTED",
                GREEN
            )
        else:
            self.set_status(
                "NBA MODE SELECTED",
                GREEN
            )

    # --------------------------------------------------
    # DATE AND LOAD BUTTON
    # --------------------------------------------------

    def build_date_section(self):

        card = GunxCard(
            size_hint_y=None,
            spacing=dp(8)
        )

        card.add_widget(Label(
            text="[b]SELECT MATCH DATE[/b]",
            markup=True,
            color=GOLD,
            size_hint_y=None,
            height=dp(24)
        ))

        self.date_input = TextInput(
            text=date.today().isoformat(),
            hint_text="YYYY-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(43),
            foreground_color=WHITE,
            background_color=(0.08, 0.10, 0.17, 1)
        )

        card.add_widget(self.date_input)

        load_button = Button(
            text="LOAD MATCHES",
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=BLUE,
            color=WHITE,
            bold=True
        )

        load_button.bind(
            on_release=lambda *_: self.load_matches()
        )

        card.add_widget(load_button)

        return card

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    def set_status(self, message, color=WHITE):

        def update(_dt):
            self.status_label.text = str(message)
            self.status_label.color = color

        Clock.schedule_once(update)

    # --------------------------------------------------
    # LOAD MATCHES
    # --------------------------------------------------

    def load_matches(self):

        key = self.api_key_input.text.strip()
        match_date = self.date_input.text.strip()

        if not key:
            self.set_status(
                "PLEASE ENTER YOUR API KEY",
                RED
            )
            return

        try:
            date.fromisoformat(match_date)
        except ValueError:
            self.set_status(
                "INVALID DATE FORMAT. USE YYYY-MM-DD",
                RED
            )
            return

        self.api_key = key
        self.fixture_container.clear_widgets()

        self.set_status(
            "CONNECTING TO API... PLEASE WAIT",
            GOLD
        )

        Thread(
            target=self.fetch_worker,
            args=(key, match_date, self.mode),
            daemon=True
        ).start()

    def fetch_worker(self, key, match_date, mode):

        try:

            if mode == "FOOTBALL":

                client = APIFootballClient(key)

                result = client.get_fixtures(match_date)

                # Football API returns a dictionary.
                if isinstance(result, dict):
                    fixtures = result.get("fixtures", [])
                else:
                    fixtures = result

            else:

                client = BasketballAPIClient(key)

                fixtures = client.get_games(match_date)

            Clock.schedule_once(
                lambda dt: self.show_matches(fixtures, mode)
            )

        except Exception as exc:

            error_message = str(exc)

            Clock.schedule_once(
                lambda dt: self.show_error(error_message)
            )

    # --------------------------------------------------
    # DISPLAY MATCHES
    # --------------------------------------------------

    def show_matches(self, results, mode):

        self.fixture_container.clear_widgets()

        if not results:
            self.set_status(
                "NO MATCHES FOUND FOR THIS DATE",
                RED
            )
            return

        self.fixtures = results

        self.set_status(
            f"{len(results)} MATCHES FOUND",
            GREEN
        )

        for fixture in results:

            if mode == "FOOTBALL":
                self.add_football_fixture(fixture)

            else:
                self.add_basketball_fixture(fixture)

    # --------------------------------------------------
    # FOOTBALL FIXTURE CARD
    # --------------------------------------------------

    def add_football_fixture(self, fixture):

        home = fixture.get("home_team", "Home")
        away = fixture.get("away_team", "Away")

        league = fixture.get("league", "Football")
        match_time = fixture.get("date", "")

        card = GunxCard()

        card.add_widget(Label(
            text=str(league),
            color=GOLD,
            font_size="12sp",
            size_hint_y=None,
            height=dp(22)
        ))

        card.add_widget(Label(
            text=f"[b]{home}[/b]  VS  [b]{away}[/b]",
            markup=True,
            color=WHITE,
            font_size="16sp",
            size_hint_y=None,
            height=dp(35)
        ))

        card.add_widget(Label(
            text=str(match_time),
            color=GREY,
            font_size="11sp",
            size_hint_y=None,
            height=dp(22)
        ))

        analyze_button = Button(
            text="ANALYZE MATCH",
            size_hint_y=None,
            height=dp(43),
            background_normal="",
            background_color=BLUE,
            color=WHITE,
            bold=True
        )

        analyze_button.bind(
            on_release=lambda *_,
            selected_fixture=fixture:
            self.analyze_football(selected_fixture)
        )

        card.add_widget(analyze_button)

        self.fixture_container.add_widget(card)

    # --------------------------------------------------
    # NBA FIXTURE CARD
    # --------------------------------------------------

    def add_basketball_fixture(self, fixture):

        teams = fixture.get("teams", {})

        home_data = teams.get("home", {})
        away_data = teams.get("away", {})

        home = home_data.get("name", "Home")
        away = away_data.get("name", "Away")

        league_data = fixture.get("league", {})
        league = league_data.get("name", "Basketball")

        card = GunxCard()

        card.add_widget(Label(
            text=str(league),
            color=GOLD,
            size_hint_y=None,
            height=dp(22)
        ))

        card.add_widget(Label(
            text=f"[b]{home}[/b] VS [b]{away}[/b]",
            markup=True,
            color=WHITE,
            font_size="16sp",
            size_hint_y=None,
            height=dp(35)
        ))

        card.add_widget(Label(
            text=str(fixture.get("date", "")),
            color=GREY,
            size_hint_y=None,
            height=dp(22)
        ))

        card.add_widget(Label(
            text="NBA ANALYSIS INTEGRATION: NEXT STEP",
            color=GOLD,
            font_size="10sp",
            size_hint_y=None,
            height=dp(25)
        ))

        self.fixture_container.add_widget(card)

    # --------------------------------------------------
    # FOOTBALL ANALYSIS
    # --------------------------------------------------

    def analyze_football(self, fixture):

        self.set_status(
            "ANALYZING MATCH... PLEASE WAIT",
            GOLD
        )

        Thread(
            target=self.analysis_worker,
            args=(fixture,),
            daemon=True
        ).start()

    def analysis_worker(self, fixture):

        try:

            client = APIFootballClient(self.api_key)

            engine = GunxFootballEngine(client)

            result = engine.analyze_fixture(fixture)

            Clock.schedule_once(
                lambda dt: self.show_analysis(result)
            )

        except Exception as exc:

            error_message = str(exc)

            Clock.schedule_once(
                lambda dt: self.show_error(error_message)
            )

    # --------------------------------------------------
    # DISPLAY ANALYSIS
    # --------------------------------------------------

    def show_analysis(self, result):

        self.fixture_container.clear_widgets()

        self.set_status(
            "ANALYSIS COMPLETED",
            GREEN
        )

        card = GunxCard()

        card.add_widget(Label(
            text="[b]GUNX MATCH ANALYSIS[/b]",
            markup=True,
            color=GOLD,
            font_size="19sp",
            size_hint_y=None,
            height=dp(40)
        ))

        for section, values in result.items():

            card.add_widget(Label(
                text=f"[b]{section}[/b]",
                markup=True,
                color=GOLD,
                font_size="14sp",
                halign="left",
                size_hint_y=None,
                height=dp(30)
            ))

            if isinstance(values, dict):

                for key, value in values.items():

                    line = Label(
                        text=f"{key}: {value}",
                        color=WHITE,
                        font_size="12sp",
                        halign="left",
                        valign="middle",
                        size_hint_y=None,
                        height=dp(28)
                    )

                    line.bind(
                        size=lambda instance, size:
                        setattr(instance, "text_size", size)
                    )

                    card.add_widget(line)

            else:

                card.add_widget(Label(
                    text=str(values),
                    color=WHITE,
                    font_size="12sp",
                    size_hint_y=None,
                    height=dp(30)
                ))

        back_button = Button(
            text="BACK TO MATCHES",
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=BLUE
        )

        back_button.bind(
            on_release=lambda *_: self.restore_matches()
        )

        card.add_widget(back_button)

        self.fixture_container.add_widget(card)

    # --------------------------------------------------
    # RESTORE MATCH LIST
    # --------------------------------------------------

    def restore_matches(self):

        self.fixture_container.clear_widgets()

        for fixture in self.fixtures:

            if self.mode == "FOOTBALL":
                self.add_football_fixture(fixture)
            else:
                self.add_basketball_fixture(fixture)

        self.set_status(
            "MATCH LIST RESTORED",
            GREEN
        )

    # --------------------------------------------------
    # ERRORS
    # --------------------------------------------------

    def show_error(self, message):

        self.set_status(
            f"ERROR: {message}",
            RED
        )

        error_card = GunxCard()

        error_card.add_widget(Label(
            text="[b]GUNX CONNECTION / ANALYSIS ERROR[/b]",
            markup=True,
            color=RED,
            size_hint_y=None,
            height=dp(35)
        ))

        error_card.add_widget(Label(
            text=str(message),
            color=WHITE,
            font_size="12sp",
            size_hint_y=None,
            height=dp(65)
        ))

        self.fixture_container.add_widget(error_card)


if __name__ == "__main__":
    GunxAnalysisApp().run()
        
