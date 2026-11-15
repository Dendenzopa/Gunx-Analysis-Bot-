
from itertools import combinations


class GunxTicketBuilder:
    """
    GUNX combined-odds ticket builder.

    Uses only supplied bookmaker odds and model probabilities.
    Never invents odds or probabilities.
    """

    def __init__(
        self,
        target_odds=3.50,
        tolerance=0.15,
        min_probability=55.0,
        max_selections=6
    ):
        self.target_odds = float(target_odds)
        self.tolerance = float(tolerance)
        self.min_probability = float(min_probability)
        self.max_selections = int(max_selections)

        if self.target_odds <= 1:
            raise ValueError("Target odds must be greater than 1.")

    def build_ticket(self, candidates):
        """
        Candidate format:
        {
            "sport": "Football",
            "fixture_id": 123,
            "match": "Team A vs Team B",
            "market": "Over 1.5",
            "selection": "Over 1.5 Goals",
            "odds": 1.35,
            "probability": 78.5,
            "data_quality": "Good"
        }
        """

        valid = []

        for item in candidates:
            try:
                odds = float(item["odds"])
                probability = float(item["probability"])
                fixture_id = item["fixture_id"]

                if odds <= 1:
                    continue

                if not 0 < probability <= 100:
                    continue

                if probability < self.min_probability:
                    continue

                if fixture_id is None:
                    continue

                if not item.get("match") or not item.get("selection"):
                    continue

                valid.append({
                    **item,
                    "odds": odds,
                    "probability": probability
                })

            except (KeyError, TypeError, ValueError):
                continue

        if not valid:
            return self._no_ticket(
                "Hakuna selections zenye data na probability "
                "zinazokidhi masharti."
            )

        # Keep the strongest candidates to control search size.
        valid.sort(
            key=lambda x: x["probability"],
            reverse=True
        )
        valid = valid[:60]

        best_ticket = None
        best_score = -1

        max_legs = min(self.max_selections, len(valid))

        for size in range(1, max_legs + 1):
            for group in combinations(valid, size):

                fixture_ids = [
                    item["fixture_id"] for item in group
                ]

                # Do not select two markets from the same fixture.
                if len(set(fixture_ids)) != len(fixture_ids):
                    continue

                combined_odds = 1.0
                combined_probability = 1.0

                for item in group:
                    combined_odds *= item["odds"]
                    combined_probability *= (
                        item["probability"] / 100
                    )

                difference = abs(
                    combined_odds - self.target_odds
                )

                if difference > self.tolerance:
                    continue

                # Prioritize probability, then closeness to target.
                closeness = 1 - (
                    difference / self.tolerance
                ) if self.tolerance > 0 else 1

                score = (
                    combined_probability * 0.85
                    + closeness * 0.15
                )

                if score > best_score:
                    best_score = score
                    best_ticket = {
                        "selections": list(group),
                        "combined_odds": round(
                            combined_odds, 3
                        ),
                        "estimated_probability": round(
                            combined_probability * 100, 2
                        ),
                        "selection_count": size,
                        "target_odds": self.target_odds
                    }

        if best_ticket is None:
            return self._no_ticket(
                "Hakuna combination yenye odds karibu na "
                f"{self.target_odds:.2f} inayokidhi kiwango "
                "cha probability. GUNX haitalazimisha tiketi."
            )

        best_ticket["status"] = "TICKET_FOUND"

        best_ticket["warning"] = (
            "Estimated probability assumes independent selections. "
            "Actual outcomes can differ. This is not a guarantee."
        )

        return best_ticket

    @staticmethod
    def _no_ticket(reason):
        return {
            "status": "NO_QUALIFIED_TICKET",
            "reason": reason,
            "selections": [],
            "combined_odds": None,
            "estimated_probability": None
              }
      
