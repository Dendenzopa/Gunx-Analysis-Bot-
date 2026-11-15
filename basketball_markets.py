
import math


class BasketballMarkets:
    """
    GUNX NBA Advanced Markets.
    Uses model estimates and bookmaker market lines.
    """

    def __init__(self, analysis):
        self.analysis = analysis

        points = analysis.get("Expected Points", {})

        self.home_points = float(points.get("Home", 0))
        self.away_points = float(points.get("Away", 0))

        self.total_points = self.home_points + self.away_points
        self.margin = self.home_points - self.away_points

        if self.home_points <= 0 or self.away_points <= 0:
            raise ValueError("Invalid expected points.")

    @staticmethod
    def normal_cdf(value, mean, deviation):
        if deviation <= 0:
            raise ValueError("Deviation must be positive.")

        z = (value - mean) / (deviation * math.sqrt(2))

        return 0.5 * (1 + math.erf(z))

    @staticmethod
    def percentage(value):
        return round(max(0, min(100, value * 100)), 2)

    def get_predictions(
        self,
        total_line=None,
        home_handicap=None
    ):
        # Approximate model assumptions.
        total_deviation = 18.0
        margin_deviation = 12.0
        team_deviation = 12.0

        result = {
            "Expected Total Points": round(
                self.total_points, 2
            ),

            "Expected Home Points": round(
                self.home_points, 2
            ),

            "Expected Away Points": round(
                self.away_points, 2
            ),

            "Home Win": self.percentage(
                1 - self.normal_cdf(
                    0, self.margin, margin_deviation
                )
            ),

            "Away Win": self.percentage(
                self.normal_cdf(
                    0, self.margin, margin_deviation
                )
            ),

            "Team Totals": {
                "Home": {
                    "Expected": round(self.home_points, 2)
                },
                "Away": {
                    "Expected": round(self.away_points, 2)
                }
            }
        }

        if total_line is not None:
            line = float(total_line)

            over = 1 - self.normal_cdf(
                line, self.total_points, total_deviation
            )

            under = 1 - over

            result["Total Points Market"] = {
                "Line": line,
                "Over": self.percentage(over),
                "Under": self.percentage(under)
            }

        if home_handicap is not None:
            handicap = float(home_handicap)

            adjusted_margin = self.margin + handicap

            home_cover = 1 - self.normal_cdf(
                0, adjusted_margin, margin_deviation
            )

            result["Handicap Market"] = {
                "Home Handicap": handicap,
                "Home Cover": self.percentage(home_cover),
                "Away Cover": self.percentage(
                    1 - home_cover
                )
            }

        result["Warning"] = (
            "Model estimates only. Standard deviations "
            "are assumptions and require historical calibration. "
            "Probabilities are not guaranteed outcomes."
        )

        return result
      
