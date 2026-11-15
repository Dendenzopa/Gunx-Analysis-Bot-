
import math


class BasketballAnalyzer:
    """
    GUNX Basketball Analysis Engine.
    Estimates team points and match probabilities.
    """

    def __init__(self, home_stats, away_stats):
        self.home_stats = home_stats or {}
        self.away_stats = away_stats or {}

    @staticmethod
    def _number(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _get_average(cls, stats, section, split):
        try:
            value = stats["points"][section]["average"][split]
            return cls._number(value)
        except (KeyError, TypeError):
            return None

    @classmethod
    def _get_games(cls, stats, split):
        try:
            value = stats["games"]["played"][split]
            return int(value)
        except (KeyError, TypeError, ValueError):
            return 0

    @staticmethod
    def _normal_cdf(value, mean, deviation):
        z = (value - mean) / (deviation * math.sqrt(2))
        return 0.5 * (1 + math.erf(z))

    def analyze_match(self, home_team, away_team):
        home_scored = self._get_average(
            self.home_stats, "for", "home"
        )
        home_conceded = self._get_average(
            self.home_stats, "against", "home"
        )

        away_scored = self._get_average(
            self.away_stats, "for", "away"
        )
        away_conceded = self._get_average(
            self.away_stats, "against", "away"
        )

        if None in (
            home_scored,
            home_conceded,
            away_scored,
            away_conceded
        ):
            raise ValueError(
                "Insufficient basketball team statistics."
            )

        home_games = self._get_games(self.home_stats, "home")
        away_games = self._get_games(self.away_stats, "away")

        if home_games < 3 or away_games < 3:
            raise ValueError(
                "Not enough home/away games for reliable analysis."
            )

        expected_home = (home_scored + away_conceded) / 2
        expected_away = (away_scored + home_conceded) / 2

        expected_total = expected_home + expected_away
        expected_margin = expected_home - expected_away

        # Approximate game-score variation.
        # This is a model assumption, not bookmaker data.
        deviation = 12.0

        home_win = 1 - self._normal_cdf(
            0, expected_margin, deviation
        )

        away_win = 1 - home_win

        home_win = max(0.0, min(1.0, home_win))
        away_win = max(0.0, min(1.0, away_win))

        if expected_home > expected_away:
            predicted_winner = home_team
        elif expected_away > expected_home:
            predicted_winner = away_team
        else:
            predicted_winner = "Balanced"

        return {
            "Match": f"{home_team} vs {away_team}",

            "Expected Points": {
                "Home": round(expected_home, 2),
                "Away": round(expected_away, 2),
                "Total": round(expected_total, 2)
            },

            "Win Probability": {
                "Home": round(home_win * 100, 2),
                "Away": round(away_win * 100, 2)
            },

            "Expected Margin": round(expected_margin, 2),

            "Predicted Winner": predicted_winner,

            "Data Quality": {
                "Home Games": home_games,
                "Away Games": away_games,
                "Status": (
                    "Limited sample"
                    if home_games < 8 or away_games < 8
                    else "Usable sample"
                )
            },

            "Warning": (
                "Statistical estimates only. "
                "Not guaranteed outcomes."
            )
        }
