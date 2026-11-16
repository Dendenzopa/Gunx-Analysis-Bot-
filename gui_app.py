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
from gunx_engine import GunxFootballEngine
from nba_data import NBADataClient


# ======================================================
# GUNX THEME
# ======================================================

BG = (0.025, 0.035, 0.075, 1)
CARD = (0.055, 0.075, 0.13, 1)
BLUE = (0.05, 0.42, 0.95, 1)
GOLD = (0.95, 0.70, 0.18, 1)
WHITE = (0.94, 0.96, 1, 1)
GREY = (0.62, 0.68, 0.78, 1)
GREEN = (0.15, 0.75, 0.43, 1)
RED = (0.85, 0.25, 0.25, 1)


# ======================================================
# GUNX CARD
# ======================================================

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


# ======================================================
# MAIN APPLICATION
# ======================================================

class GunxAnalysisApp(App):

    def build(self):

        Window.clearcolor = BG

        self.mode = "FOOTBALL"
        self.api_key = ""
        self.fixtures = []

        self.current_date = date.today().isoformat()

        self.nba_fetching = False
        self.nba_loaded = False

        self.fixture_container = None
        self.status_label = None

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
            height=dp(28),
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

        # Automatic NBA refresh every 30 seconds.
        Clock.schedule_interval(
            self.refresh_nba_scores,
            30
        )

        return root

    # ==================================================
    # HEADER
    # ==================================================

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
            text="THE PULSE OF GLOBAL SPORTS ANALYSIS",
            color=GREY,
            font_size="10sp",
            size_hint_y=None,
            height=dp(25)
        )

        header.add_widget(subtitle)

        return header

    # ==================================================
    # FOOTBALL API SECTION
    # ==================================================

    def build_api_section(self):

        card = GunxCard(
            spacing=dp(7)
        )

        card.add_widget(Label(
            text="[b]FOOTBALL API CONNECTION[/b]",
            markup=True,
            color=GOLD,
            size_hint_y=None,
            height=dp(25)
        ))

        self.api_key_input = TextInput(
            hint_text="Football API-Sports key (NBA needs no key)",
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

    # ==================================================
    # NAVIGATION
    # ==================================================

    def build_navigation(self):

        nav = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )

        self.football_button = Button(
            text="FOOTBALL",
            background_normal="",
            background_color=BLUE,
            color=WHITE,
            bold=True
        )

        self.nba_button = Button(
            text="NBA",
            background_normal="",
            background_color=CARD,
            color=GOLD,
            bold=True
        )

        self.football_button.bind(
            on_release=lambda *_: self.change_mode("FOOTBALL")
        )

        self.nba_button.bind(
            on_release=lambda *_: self.change_mode("NBA")
        )

        nav.add_widget(self.football_button)
        nav.add_widget(self.nba_button)

        return nav

    def change_mode(self, mode):

        self.mode = mode

        self.fixture_container.clear_widgets()

        if mode == "FOOTBALL":

            self.football_button.background_color = BLUE
            self.nba_button.background_color = CARD

            self.set_status(
                "FOOTBALL MODE SELECTED",
                GREEN
            )

        else:

            self.nba_button.background_color = BLUE
            self.football_button.background_color = CARD

            self.set_status(
                "NBA MODE SELECTED - NO API KEY REQUIRED",
                GREEN
            )

    # ==================================================
    # DATE SECTION
    # ==================================================

    def build_date_section(self):

        card = GunxCard(
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

    # ==================================================
    # STATUS
    # ==================================================

    def set_status(self, message, color=WHITE):

        def update(_dt):

            if self.status_label:
                self.status_label.text = str(message)
                self.status_label.color = color

        Clock.schedule_once(update)

    # ==================================================
    # LOAD MATCHES
    # ==================================================

    def load_matches(self):

        match_date = self.date_input.text.strip()

        try:
            date.fromisoformat(match_date)

        except ValueError:

            self.set_status(
                "INVALID DATE. USE YYYY-MM-DD",
                RED
            )
            return

        key = self.api_key_input.text.strip()

        if self.mode == "FOOTBALL" and not key:

            self.set_status(
                "PLEASE ENTER FOOTBALL API KEY",
                RED
            )
            return

        self.api_key = key
        self.current_date = match_date

        self.fixture_container.clear_widgets()

        if self.mode == "NBA":
            self.nba_loaded = True

        self.set_status(
            "LOADING MATCHES...",
            GOLD
        )

        Thread(
            target=self.fetch_worker,
            args=(key, match_date, self.mode),
            daemon=True
        ).start()

    # ==================================================
    # FETCH WORKER
    # ==================================================

    def fetch_worker(self, key, match_date, mode):

        try:

            if mode == "FOOTBALL":

                client = APIFootballClient(key)

                result = client.get_fixtures(match_date)

                if isinstance(result, dict):
                    fixtures = result.get("fixtures", [])
                else:
                    fixtures = result

            else:

                client = NBADataClient()

                fixtures = client.get_games(match_date)

            Clock.schedule_once(
                lambda dt: self.show_matches(fixtures, mode)
            )

        except Exception as exc:

            error_message = str(exc)

            Clock.schedule_once(
                lambda dt: self.show_error(error_message)
            )

    # ==================================================
    # DISPLAY MATCHES
    # ==================================================

    def show_matches(self, results, mode):

        if mode != self.mode:
            return

        self.fixture_container.clear_widgets()

        self.fixtures = results or []

        if not self.fixtures:

            self.set_status(
                "NO MATCHES FOUND FOR THIS DATE",
                RED
            )
            return

        self.set_status(
            f"{len(self.fixtures)} MATCHES FOUND",
            GREEN
        )

        for fixture in self.fixtures:

            if mode == "FOOTBALL":
                self.add_football_fixture(fixture)

            else:
                self.add_basketball_fixture(fixture)

    # ==================================================
    # FOOTBALL FIXTURE CARD
    # ==================================================

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

    # ==================================================
    # NBA FIXTURE CARD
    # ==================================================

    def add_basketball_fixture(self, fixture):

        home = fixture.get("home_team", "Home")
        away = fixture.get("away_team", "Away")

        home_score = fixture.get("home_score")
        away_score = fixture.get("away_score")

        status = fixture.get(
            "status_detail",
            "SCHEDULED"
        )

        period = fixture.get("period")
        clock = fixture.get("clock")

        if home_score is not None and away_score is not None:
            score_text = f"{away_score}  -  {home_score}"
        else:
            score_text = "VS"

        game_status = str(status).upper()

        if fixture.get("status") == "in":

            game_status = "LIVE | " + game_status
            status_color = GREEN

        elif fixture.get("status") == "post":

            game_status = "FINISHED"
            status_color = GREY

        else:

            status_color = GOLD

        if period:
            game_status += f" | PERIOD {period}"

        if clock:
            game_status += f" | {clock}"

        card = GunxCard()

        card.add_widget(Label(
            text="NBA",
            color=GOLD,
            font_size="12sp",
            size_hint_y=None,
            height=dp(22)
        ))

        card.add_widget(Label(
            text=f"[b]{away}[/b] VS [b]{home}[/b]",
            markup=True,
            color=WHITE,
            font_size="15sp",
            size_hint_y=None,
            height=dp(35)
        ))

        card.add_widget(Label(
            text=score_text,
            color=WHITE,
            font_size="23sp",
            bold=True,
            size_hint_y=None,
            height=dp(40)
        ))

        card.add_widget(Label(
            text=game_status,
            color=status_color,
            font_size="11sp",
            size_hint_y=None,
            height=dp(25)
        ))

        card.add_widget(Label(
            text=str(fixture.get("date", "")),
            color=GREY,
            font_size="10sp",
            size_hint_y=None,
            height=dp(22)
        ))

        self.fixture_container.add_widget(card)

    # ==================================================
    # FOOTBALL ANALYSIS
    # ==================================================

    def analyze_football(self, fixture):

        if self.mode != "FOOTBALL":
            return

        self.set_status(
            "GUNX ANALYZING MATCH...",
            GOLD
        )

        Thread(
            target=self.analysis_worker,
            args=(fixture,),
            daemon=True
        ).start()

    def analysis_worker(self, fixture):

        try:

            engine = GunxFootballEngine(self.api_key)

            result = engine.analyze_fixture(fixture)

            Clock.schedule_once(
                lambda dt: self.show_analysis(result)
            )

        except Exception as exc:

            error_message = str(exc)

            Clock.schedule_once(
                lambda dt: self.show_error(error_message)
            )

    # ==================================================
    # DISPLAY FOOTBALL ANALYSIS
    # ==================================================

    def show_analysis(self, result):

        if self.mode != "FOOTBALL":
            return

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

    # ==================================================
    # RESTORE MATCH LIST
    # ==================================================

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

    # ==================================================
    # NBA AUTOMATIC LIVE REFRESH
    # ==================================================

    def refresh_nba_scores(self, dt):

        if self.mode != "NBA":
            return

        if not self.nba_loaded:
            return

        if self.nba_fetching:
            return

        self.nba_fetching = True

        Thread(
            target=self.nba_refresh_worker,
            daemon=True
        ).start()

    def nba_refresh_worker(self):

        try:

            client = NBADataClient()

            games = client.get_games(
                self.current_date
            )

            Clock.schedule_once(
                lambda dt: self.update_nba_scores(games)
            )

        except Exception as exc:

            error_message = str(exc)

            Clock.schedule_once(
                lambda dt: self.finish_nba_refresh(error_message)
            )

    def update_nba_scores(self, games):

        self.nba_fetching = False

        if self.mode != "NBA":
            return

        self.fixtures = games or []
        self.fixture_container.clear_widgets()

        if not self.fixtures:
            self.set_status(
                "NO NBA GAMES FOUND",
                RED
            )
            return

        self.set_status(
            f"{len(self.fixtures)} NBA GAMES FOUND",
            GREEN
        )

        for game in self.fixtures:
            self.add_basketball_fixture(game)

    def finish_nba_refresh(self, error_message):

        self.nba_fetching = False

        if self.mode == "NBA":
            self.set_status(
                f"NBA REFRESH ERROR: {error_message}",
                RED
            )


if __name__ == "__main__":
    GunxAnalysisApp().run()
