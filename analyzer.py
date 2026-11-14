import math


class GunxMatchAnalyzer:
    """
    GUNX ANALYSIS BOT
    Football probability engine using the Poisson model.

    Note:
    This model estimates probabilities from expected goals.
    It does not guarantee match results.
    """

    def __init__(
        self,
        home_team,
        away_team,
        home_avg_goals,
        away_avg_goals,
        max_goals=20
    ):
        self.home_team = str(home_team).strip()
        self.away_team = str(away_team).strip()

        self.home_lambda = float(home_avg_goals)
        self.away_lambda = float(away_avg_goals)
        self.max_goals = int(max_goals)

        if not self.home_team or not self.away_team:
            raise ValueError("Majina ya timu yanahitajika.")

        if not math.isfinite(self.home_lambda):
            raise ValueError("Wastani wa magoli ya nyumbani si sahihi.")

        if not math.isfinite(self.away_lambda):
            raise ValueError("Wastani wa magoli ya ugenini si sahihi.")

        if self.home_lambda < 0 or self.away_lambda < 0:
            raise ValueError("Wastani wa magoli hauwezi kuwa chini ya sifuri.")

        if self.max_goals < 5:
            raise ValueError("max_goals lazima iwe angalau 5.")

    @staticmethod
    def calculate_poisson_probability(expected_goals, goals):
        """Calculate probability of a team scoring a given number of goals."""
        if expected_goals < 0 or goals < 0:
            return 0.0

        if expected_goals == 0:
            return 1.0 if goals == 0 else 0.0

        return (
            math.exp(-expected_goals)
            * (expected_goals ** goals)
            / math.factorial(goals)
        )

    @staticmethod
    def format_probability(probability):
        return f"{probability * 100:.1f}%"

    def _build_score_matrix(self):
        """Create and normalize the possible score probability matrix."""
        matrix = []
        total_probability = 0.0

        for home_goals in range(self.max_goals + 1):
            row = []

            home_probability = self.calculate_poisson_probability(
                self.home_lambda, home_goals
            )

            for away_goals in range(self.max_goals + 1):
                away_probability = self.calculate_poisson_probability(
                    self.away_lambda, away_goals
                )

                probability = home_probability * away_probability
                row.append(probability)
                total_probability += probability

            matrix.append(row)

        if total_probability <= 0:
            raise ValueError("Imeshindikana kukokotoa probabilities.")

        # Normalize to account for the tiny probability tail beyond max_goals.
        return [
            [probability / total_probability for probability in row]
            for row in matrix
        ]

    def analyze_match(self):
        matrix = self._build_score_matrix()

        home_win = 0.0
        draw = 0.0
        away_win = 0.0
        gg = 0.0
        over_15 = 0.0
        over_25 = 0.0
        over_35 = 0.0
        under_35 = 0.0

        score_probabilities = []

        for home_goals, row in enumerate(matrix):
            for away_goals, probability in enumerate(row):

                if home_goals > away_goals:
                    home_win += probability
                elif home_goals == away_goals:
                    draw += probability
                else:
                    away_win += probability

                total_goals = home_goals + away_goals

                if home_goals > 0 and away_goals > 0:
                    gg += probability

                if total_goals >= 2:
                    over_15 += probability

                if total_goals >= 3:
                    over_25 += probability

                if total_goals >= 4:
                    over_35 += probability
                else:
                    under_35 += probability

                score_probabilities.append(
                    (probability, home_goals, away_goals)
                )

        # Most likely exact score.
        score_probabilities.sort(reverse=True)
        best_score = score_probabilities[0]

        ng = 1.0 - gg

        double_chance = {
            "1X": home_win + draw,
            "12": home_win + away_win,
            "X2": draw + away_win
        }

        best_double_chance = max(
            double_chance,
            key=double_chance.get
        )

        strongest_1x2 = max(
            {
                "Home Win": home_win,
                "Draw": draw,
                "Away Win": away_win
            },
            key=lambda item: {
                "Home Win": home_win,
                "Draw": draw,
                "Away Win": away_win
            }[item]
        )

        highest_probability = max(home_win, draw, away_win)

        if highest_probability >= 0.60:
            risk = "Model uncertainty: Lower"
        elif highest_probability >= 0.45:
            risk = "Model uncertainty: Medium"
        else:
            risk = "Model uncertainty: High"

        expected_total = self.home_lambda + self.away_lambda

        return {
            "Match": f"{self.home_team} vs {self.away_team}",

            "1X2 Probability": {
                "Home Win": self.format_probability(home_win),
                "Draw": self.format_probability(draw),
                "Away Win": self.format_probability(away_win),
                "Most Likely 1X2": strongest_1x2
            },

            "Double Chance": {
                "1X": self.format_probability(double_chance["1X"]),
                "12": self.format_probability(double_chance["12"]),
                "X2": self.format_probability(double_chance["X2"]),
                "Best Double Chance": best_double_chance
            },

            "GG / NG": {
                "GG": self.format_probability(gg),
                "NG": self.format_probability(ng)
            },

            "Over / Under 1.5": {
                "Over 1.5": self.format_probability(over_15),
                "Under 1.5": self.format_probability(1.0 - over_15)
            },

            "Over / Under 2.5": {
                "Over 2.5": self.format_probability(over_25),
                "Under 2.5": self.format_probability(1.0 - over_25)
            },

            "Over / Under 3.5": {
                "Over 3.5": self.format_probability(over_35),
                "Under 3.5": self.format_probability(under_35)
            },

            "Most Likely Score": (
                f"{best_score[1]} - {best_score[2]}"
            ),

            "Expected Goals": {
                self.home_team: round(self.home_lambda, 2),
                self.away_team: round(self.away_lambda, 2),
                "Total": round(expected_total, 2)
            },

            "Risk Assessment": risk
        }
