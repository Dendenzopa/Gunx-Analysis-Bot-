
from analyzer import GunxMatchAnalyzer
from markets import AdvancedMarkets


class GunxFootballEngine:
    """
    GUNX Football Analysis Engine.
    Extracts team statistics and estimates match probabilities.
    """

    def __init__(self, api_client):
        self.api = api_client

    @staticmethod
    def number(value):
        try:
            if value in (None, "", "-"):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def extract(stats, section, metric, split):
        try:
            value = stats[section][metric]["average"][split]
            return GunxFootballEngine.number(value)
        except (KeyError, TypeError):
            return None

    @staticmethod
    def games_played(stats, split):
        try:
            return int(stats["fixtures"]["played"][split])
        except (KeyError, TypeError, ValueError):
            return 0

    def analyze_fixture(self, fixture):
        home_id = fixture.get("home_team_id")
        away_id = fixture.get("away_team_id")
        league_id = fixture.get("league_id")
        season = fixture.get("season")

        home_name = fixture.get("home_team", "Home")
        away_name = fixture.get("away_team", "Away")

        if not all((home_id, away_id, league_id, season)):
            raise ValueError("Fixture is missing team, league or season IDs.")

        home_stats = self.api.get_team_statistics(
            league_id, season, home_id
        )

        away_stats = self.api.get_team_statistics(
            league_id, season, away_id
        )

        home_scored = self.extract(
            home_stats, "goals", "for", "home"
        )
        home_conceded = self.extract(
            home_stats, "goals", "against", "home"
        )

        away_scored = self.extract(
            away_stats, "goals", "for", "away"
        )
        away_conceded = self.extract(
            away_stats, "goals", "against", "away"
        )

        home_games = self.games_played(home_stats, "home")
        away_games = self.games_played(away_stats, "away")

        values = (
            home_scored,
            home_conceded,
            away_scored,
            away_conceded
        )

        if any(value is None for value in values):
            raise ValueError(
                "Team goal statistics are incomplete."
            )

        if home_games < 5 or away_games < 5:
            raise ValueError(
                "Insufficient home/away match history."
            )

        home_lambda = (home_scored + away_conceded) / 2
        away_lambda = (away_scored + home_conceded) / 2

        analyzer = GunxMatchAnalyzer(
            home_name,
            away_name,
            home_lambda,
            away_lambda
        )

        analysis = analyzer.analyze_match()

        advanced = AdvancedMarkets(
            home_name,
            away_name,
            home_lambda,
            away_lambda
        )

        analysis["Advanced Markets"] = (
            advanced.get_advanced_predictions()
        )

        analysis["Data Quality"] = {
            "Home Games": home_games,
            "Away Games": away_games,
            "Status": (
                "Usable sample"
                if home_games >= 8 and away_games >= 8
                else "Limited sample"
            )
        }

        analysis["Warning"] = (
            "GUNX statistical estimates only. "
            "Not guaranteed match outcomes."
        )

        return analysis
      
