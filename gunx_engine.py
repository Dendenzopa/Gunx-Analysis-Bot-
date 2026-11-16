
from api import APIFootballClient
from analyzer import GunxMatchAnalyzer
from markets import AdvancedMarkets


class GunxFootballEngine:
    """
    GUNX Football Automatic Analysis Engine.

    Fetches team statistics and estimates expected goals.
    It does not invent bookmaker odds.
    """

    def __init__(self, api_key):
        self.client = APIFootballClient(api_key)
        self.stats_cache = {}

    @staticmethod
    def _number(value):
        try:
            if value in (None, "", "-"):
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _unwrap_stats(data):
        if isinstance(data, dict) and "response" in data:
            return data["response"]
        return data if isinstance(data, dict) else {}

    def _get_team_stats(self, league_id, season, team_id):
        cache_key = (league_id, season, team_id)

        if cache_key not in self.stats_cache:
            data = self.client.get_team_statistics(
                league_id=league_id,
                season=season,
                team_id=team_id
            )
            self.stats_cache[cache_key] = self._unwrap_stats(data)

        return self.stats_cache[cache_key]

    def _extract_average(self, stats, section, kind, split):
        try:
            value = stats["goals"][section][kind][split]
            return self._number(value)
        except (KeyError, TypeError):
            return None

    def _extract_games(self, stats, split):
        try:
            value = stats["fixtures"]["played"][split]
            return int(value)
        except (KeyError, TypeError, ValueError):
            return 0

    def analyze_fixture(self, fixture):
        home_name = fixture.get("home_team", "Home")
        away_name = fixture.get("away_team", "Away")

        league_id = fixture.get("league_id")
        season = fixture.get("season")
        home_id = fixture.get("home_team_id")
        away_id = fixture.get("away_team_id")

        if not all((league_id, season, home_id, away_id)):
            raise ValueError(
                "Fixture is missing league, season or team IDs."
            )

        home_stats = self._get_team_stats(
            league_id, season, home_id
        )
        away_stats = self._get_team_stats(
            league_id, season, away_id
        )

        home_scored = self._extract_average(
            home_stats, "for", "average", "home"
        )
        home_conceded = self._extract_average(
            home_stats, "against", "average", "home"
        )
        away_scored = self._extract_average(
            away_stats, "for", "average", "away"
        )
        away_conceded = self._extract_average(
            away_stats, "against", "average", "away"
        )

        values = (
            home_scored,
            home_conceded,
            away_scored,
            away_conceded
        )

        if any(value is None for value in values):
            raise ValueError(
                "API haijarudisha wastani wa magoli unaohitajika."
            )

        home_games = self._extract_games(home_stats, "home")
        away_games = self._extract_games(away_stats, "away")

        if home_games < 3 or away_games < 3:
            raise ValueError(
                "Takwimu za nyumbani/ugenini hazitoshi."
            )

        # Combine attacking and defensive averages.
        home_lambda = (home_scored + away_conceded) / 2
        away_lambda = (away_scored + home_conceded) / 2

        analyzer = GunxMatchAnalyzer(
            home_team=home_name,
            away_team=away_name,
            home_avg_goals=home_lambda,
            away_avg_goals=away_lambda
        )

        analysis = analyzer.analyze_match()

        advanced = AdvancedMarkets(
            home_team=home_name,
            away_team=away_name,
            home_lambda=home_lambda,
            away_lambda=away_lambda
        ).get_advanced_predictions()

        return {
            "fixture_id": fixture.get("fixture_id"),
            "match": f"{home_name} vs {away_name}",
            "league": fixture.get("league", ""),
            "analysis": analysis,
            "advanced_markets": advanced,
            "data_quality": {
                "home_games": home_games,
                "away_games": away_games,
                "status": (
                    "LIMITED SAMPLE"
                    if home_games < 8 or away_games < 8
                    else "USABLE SAMPLE"
                )
            },
            "bookmaker_odds": (
                "NOT CONNECTED: real bookmaker odds are not yet fetched."
            ),
            "warning": (
                "Model estimates only. Football results are uncertain."
            )
        }

    def analyze_fixtures(self, fixtures):
        results = []

        for fixture in fixtures:
            try:
                results.append({
                    "status": "SUCCESS",
                    "result": self.analyze_fixture(fixture)
                })
            except Exception as exc:
                results.append({
                    "status": "SKIPPED",
                    "match": (
                        str(fixture.get("home_team", "Home"))
                        + " vs "
                        + str(fixture.get("away_team", "Away"))
                    ),
                    "reason": str(exc)
                })

        return results
      
