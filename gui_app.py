
import os
import math
from datetime import date
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex

from analyzer import GunxMatchAnalyzer
from markets import AdvancedMarkets
from api import APIFootballClient, APIFootballError


# ==========================================
# GUNX COLORS
# ==========================================

BLACK = "#08090B"
DARK = "#111318"
PANEL = "#171A20"
GOLD = "#FFC928"
GOLD_DARK = "#A87900"
WHITE = "#F5F5F5"
GREY = "#AEB3BD"
GREEN = "#00C853"
BLUE = "#087BFF"
RED = "#FF4545"


# ==========================================
# REUSABLE PANEL
# ==========================================

class GunxPanel(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.padding = dp(12)
        self.spacing = dp(8)

        with self.canvas.before:
            self.bg_color = Color(
                *get_color_from_hex(PANEL)
            )
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

            self.border_color = Color(
                *get_color_from_hex(GOLD_DARK)
            )
            self.border_line = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(14)
                ),
                width=1.2
            )

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas
        )

    def update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        self.border_line.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(14)
        )


# ==========================================
# MAIN APPLICATION
# ==========================================

class GunxAnalysisApp(App):

    def build(self):

        self.title = "GUNX ANALYSIS BOT"
        Window.clearcolor = get_color_from_hex(BLACK)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(9),
            spacing=dp(8)
        )

        # MAIN SCROLL VIEW
        scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(3)
        )

        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(3), dp(5)],
            size_hint_y=None
        )

        self.content.bind(
            minimum_height=self.content.setter("height")
        )

        # ==================================
        # HEADER / LOGO
        # ==================================

        header = GunxPanel(
            orientation="vertical",
            size_hint_y=None,
            height=dp(175),
            padding=dp(10),
            spacing=dp(3)
        )

        logo_path = os.path.join(
            os.path.dirname(__file__),
            "gunx_logo.png"
        )

        if os.path.exists(logo_path):

            logo = Image(
                source=logo_path,
                size_hint_y=None,
                height=dp(95),
                allow_stretch=True,
                keep_ratio=True
            )
            header.add_widget(logo)

        else:

            logo_title = Label(
                text="[b][color=FFC928]GUNX[/color][/b]",
                markup=True,
                font_size="42sp",
                size_hint_y=None,
                height=dp(65)
            )
            header.add_widget(logo_title)

        subtitle = Label(
            text="[b][color=FFFFFF]ANALYSIS BOT[/color][/b]",
            markup=True,
            font_size="23sp",
            size_hint_y=None,
            height=dp(35)
        )
        header.add_widget(subtitle)

        tagline = Label(
            text="[color=FFC928]ANALYZE  •  PREDICT  •  WIN[/color]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=dp(25)
        )
        header.add_widget(tagline)

        self.content.add_widget(header)

        intro = Label(
            text="[b][color=FFC928]GLOBAL FOOTBALL ANALYSIS[/color][/b]\n"
                 "[color=AAAAAA]Advanced Statistical Predictions[/color]",
            markup=True,
            font_size="15sp",
            size_hint_y=None,
            height=dp(55)
        )
        self.content.add_widget(intro)

        # ==================================
        # API CONNECTION
        # ==================================

        api_panel = self.create_section(
            "API CONNECTION",
            "Ingiza API-Football Key yako"
        )

        self.api_key_input = TextInput(
            hint_text="API-Football Key",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size="14sp",
            foreground_color=get_color_from_hex(WHITE),
            hint_text_color=get_color_from_hex(GREY),
            cursor_color=get_color_from_hex(GOLD),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex(DARK),
            padding=[dp(12), dp(13)]
        )
        api_panel.add_widget(self.api_key_input)

        date_label = self.make_label(
            "MATCH DATE",
            size=13,
            color=GOLD
        )
        api_panel.add_widget(date_label)

        self.date_input = TextInput(
            text=date.today().isoformat(),
            hint_text="YYYY-MM-DD",
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size="15sp",
            foreground_color=get_color_from_hex(WHITE),
            cursor_color=get_color_from_hex(GOLD),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex(DARK),
            padding=[dp(12), dp(12)]
        )
        api_panel.add_widget(self.date_input)

        fetch_button = self.make_button(
            "TAFUTA MECHI ZA TAREHE HII",
            BLUE
        )
        fetch_button.bind(
            on_press=self.fetch_fixtures
        )
        api_panel.add_widget(fetch_button)

        self.content.add_widget(api_panel)

        # ==================================
        # FIXTURES
        # ==================================

        fixtures_panel = self.create_section(
            "TODAY'S FIXTURES",
            "Tafuta mechi kupitia API-Football"
        )

        fixtures_note = self.make_label(
            "Matokeo ya mechi ulizotafuta yataonekana kwenye RESULTS.",
            size=12,
            color=GREY
        )
        fixtures_panel.add_widget(fixtures_note)

        self.content.add_widget(fixtures_panel)

        # ==================================
        # MATCH ANALYSIS
        # ==================================

        analysis_panel = self.create_section(
            "MATCH ANALYSIS",
            "Ingiza taarifa za timu"
        )

        self.home_entry = self.add_field(
            analysis_panel,
            "HOME TEAM",
            "Simba SC"
        )

        self.away_entry = self.add_field(
            analysis_panel,
            "AWAY TEAM",
            "Yanga SC"
        )

        self.home_goals = self.add_field(
            analysis_panel,
            "HOME AVERAGE GOALS",
            "1.7"
        )

        self.away_goals = self.add_field(
            analysis_panel,
            "AWAY AVERAGE GOALS",
            "1.5"
        )

        analyze_button = self.make_button(
            "CHAMBUA MECHI",
            GREEN,
            text_color=BLACK
        )

        analyze_button.bind(
            on_press=self.analyze_match
        )

        analysis_panel.add_widget(analyze_button)

        self.content.add_widget(analysis_panel)

        # ==================================
        # RESULTS
        # ==================================

        results_panel = self.create_section(
            "GUNX RESULTS",
            "Statistical analysis and predictions"
        )

        self.output = TextInput(
            text=(
                "KARIBU GUNX ANALYSIS BOT\n"
                "================================\n\n"
                "1. Ingiza API Key kutafuta fixtures.\n\n"
                "2. Ingiza majina ya timu.\n\n"
                "3. Weka wastani wa magoli.\n\n"
                "4. Bonyeza CHAMBUA MECHI.\n\n"
                "Matokeo yataonekana hapa."
            ),
            readonly=True,
            multiline=True,
            size_hint_y=None,
            height=dp(440),
            font_size="14sp",
            foreground_color=get_color_from_hex(WHITE),
            cursor_color=get_color_from_hex(GOLD),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex(BLACK),
            padding=[dp(12), dp(12)]
        )

        results_panel.add_widget(self.output)
        self.content.add_widget(results_panel)

        # ==================================
        # FOOTER
        # ==================================

        footer = Label(
            text="[b][color=FFC928]GUNX ANALYSIS BOT[/color][/b]\n"
                 "[color=AAAAAA]Football Statistical Intelligence[/color]",
            markup=True,
            font_size="13sp",
            size_hint_y=None,
            height=dp(55)
        )

        self.content.add_widget(footer)

        scroll.add_widget(self.content)
        root.add_widget(scroll)

        return root

    # ======================================
    # UI HELPERS
    # ======================================

    def make_label(self, text, size=14, color=WHITE):

        return Label(
            text=f"[color={color.replace('#', '')}]{text}[/color]",
            markup=True,
            font_size=f"{size}sp",
            size_hint_y=None,
            height=dp(30),
            halign="left",
            valign="middle"
        )

    def create_section(self, title, description=""):

        panel = GunxPanel(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(12),
            spacing=dp(8)
        )

        panel.bind(
            minimum_height=panel.setter("height")
        )

        heading = Label(
            text=f"[b][color=FFC928]{title}[/color][/b]",
            markup=True,
            font_size="17sp",
            size_hint_y=None,
            height=dp(35),
            halign="left",
            valign="middle"
        )

        heading.bind(
            size=lambda instance, size:
            setattr(instance, "text_size", size)
        )

        panel.add_widget(heading)

        if description:

            desc = Label(
                text=f"[color=AAAAAA]{description}[/color]",
                markup=True,
                font_size="12sp",
                size_hint_y=None,
                height=dp(25),
                halign="left"
            )

            panel.add_widget(desc)

        return panel

    def make_button(
        self,
        text,
        color=GOLD,
        text_color=WHITE
    ):

        button = Button(
            text=text,
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_down="",
            background_color=get_color_from_hex(color),
            color=get_color_from_hex(text_color),
            font_size="15sp",
            bold=True
        )

        return button

    def add_field(
        self,
        layout,
        label_text,
        default_value
    ):

        label = self.make_label(
            label_text,
            size=12,
            color=GOLD
        )

        layout.add_widget(label)

        field = TextInput(
            text=default_value,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            font_size="15sp",
            foreground_color=get_color_from_hex(WHITE),
            hint_text_color=get_color_from_hex(GREY),
            cursor_color=get_color_from_hex(GOLD),
            background_normal="",
            background_active="",
            background_color=get_color_from_hex(DARK),
            padding=[dp(12), dp(12)]
        )

        layout.add_widget(field)

        return field

    # ======================================
    # OUTPUT
    # ======================================

    def set_output(self, message):
        self.output.text = str(message)
        self.output.cursor = (0, 0)

    # ======================================
    # API FIXTURES
    # ======================================

    def fetch_fixtures(self, instance):

        api_key = self.api_key_input.text.strip()
        match_date = self.date_input.text.strip()

        if not api_key:

            self.set_output(
                "KOSA: Tafadhali ingiza API Key."
            )
            return

        try:
            date.fromisoformat(match_date)

        except ValueError:

            self.set_output(
                "KOSA: Tarehe iwe YYYY-MM-DD."
            )
            return

        self.set_output(
            "GUNX API CONNECTION\n\n"
            "Inatafuta mechi...\n"
            "Tafadhali subiri."
        )

        Thread(
            target=self.fetch_fixtures_worker,
            args=(api_key, match_date),
            daemon=True
        ).start()

    def fetch_fixtures_worker(
        self,
        api_key,
        match_date
    ):

        try:

            client = APIFootballClient(api_key)

            result = client.get_fixtures(
                match_date=match_date
            )

            fixtures = result.get("fixtures", [])

            lines = [
                "GUNX GLOBAL FIXTURES",
                "=" * 38,
                f"TAREHE: {match_date}",
                f"MECHI ZILIZOPATIKANA: {len(fixtures)}",
                ""
            ]

            for number, match in enumerate(
                fixtures,
                start=1
            ):

                home = match.get("home_team") or "Unknown"
                away = match.get("away_team") or "Unknown"
                league = match.get("league") or "Unknown League"
                country = match.get("country") or "Unknown Country"
                kickoff = match.get("date") or "Unknown"
                status = match.get("status") or "Unknown"

                lines.extend([
                    f"{number}. {home} vs {away}",
                    f"Ligi: {league}",
                    f"Nchi: {country}",
                    f"Muda: {kickoff}",
                    f"Hali: {status}",
                    "-" * 35
                ])

            if not fixtures:

                lines.append(
                    "Hakuna mechi zilizopatikana kwa tarehe hiyo."
                )

            message = "\n".join(lines)

        except (APIFootballError, ValueError) as error:

            message = f"API ERROR:\n{error}"

        except Exception as error:

            message = f"HITILAFU:\n{error}"

        Clock.schedule_once(
            lambda dt: self.set_output(message)
        )

    # ======================================
    # FOOTBALL ANALYSIS
    # ======================================

    def analyze_match(self, instance):

        home = self.home_entry.text.strip()
        away = self.away_entry.text.strip()

        if not home or not away:

            self.set_output(
                "KOSA: Jaza majina ya timu zote mbili."
            )
            return

        try:

            home_goals = float(self.home_goals.text)
            away_goals = float(self.away_goals.text)

            if (
                not math.isfinite(home_goals)
                or not math.isfinite(away_goals)
                or home_goals < 0
                or away_goals < 0
            ):
                raise ValueError

            analyzer = GunxMatchAnalyzer(
                home,
                away,
                home_goals,
                away_goals
            )

            analysis = analyzer.analyze_match()

            advanced_bot = AdvancedMarkets(
                home,
                away,
                home_goals,
                away_goals
            )

            advanced = (
                advanced_bot.get_advanced_predictions()
            )

            lines = [
                "GUNX MATCH ANALYSIS",
                "=" * 38,
                analysis["Match"],
                "",
                "1X2 PROBABILITY",
                "-" * 30
            ]

            for market, probability in (
                analysis["1X2 Probability"].items()
            ):

                lines.append(
                    f"{market}: {probability}"
                )

            lines.extend([
                "",
                "DOUBLE CHANCE",
                "-" * 30
            ])

            for market, probability in (
                analysis["Double Chance"].items()
            ):

                lines.append(
                    f"{market}: {probability}"
                )

            lines.extend([
                "",
                "GOALS MARKETS",
                "-" * 30
            ])

            for market, probability in (
                analysis["GG / NG"].items()
            ):

                lines.append(
                    f"{market}: {probability}"
                )

            for market, probability in (
                analysis["Over / Under 1.5"].items()
            ):

                lines.append(
                    f"{market}: {probability}"
                )

            for market, probability in (
                analysis["Over / Under 2.5"].items()
            ):

                lines.append(
                    f"{market}: {probability}"
                )

            for market, probability in (
                analysis["Over / Under 3.5"].items()
            ):

                lines.append(
                    f"{market}: {probability}"
                )

            lines.extend([
                "",
                "SCORE & EXPECTED GOALS",
                "-" * 30,
                f"Most Likely Score: {analysis['Most Likely Score']}",
                f"Expected Goals: {analysis['Expected Goals']['Total']}",
                "",
                "ADVANCED MARKETS",
                "-" * 30,
                f"HT/FT: {advanced['HT/FT Prediction']}",
                f"Goal Range: {advanced['Recommended Goal Range']}",
                f"Corners: {advanced['Estimated Corners']}",
                f"Cards: {advanced['Booking Points / Cards']}",
                "",
                f"MODEL RISK: {analysis['Risk Assessment']}",
                "",
                "DISCLAIMER",
                "Makadirio ya modeli si uhakika wa matokeo."
            ])

            self.set_output(
                "\n".join(lines)
            )

        except ValueError:

            self.set_output(
                "KOSA: Weka wastani wa magoli kama namba "
                "sahihi zisizo chini ya sifuri."
            )

        except Exception as error:

            self.set_output(
                f"HITILAFU YA UCHAMBUZI:\n{error}"
            )


if __name__ == "__main__":

    GunxAnalysisApp().run()
