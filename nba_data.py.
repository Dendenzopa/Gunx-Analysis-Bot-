
import json
import urllib.parse
import urllib.request
import urllib.error


class NBADataError(Exception):
    """GUNX NBA data source error."""


class NBADataClient:
    """
    GUNX NBA data client.
    Uses ESPN's public scoreboard endpoint.
    No API key required.
    """

    BASE_URL = (
        "https://site.api.espn.com/apis/site/v2/"
        "sports/basketball/nba/scoreboard"
    )

    def __init__(self, timeout=20):
        self.timeout = timeout

    def _request(self, params=None):
        params = params or {}

        query = urllib.parse.urlencode(params)
        url = self.BASE_URL

        if query:
            url += "?" + query

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 GUNX-Analysis-Bot",
                "Accept": "application/json"
            },
            method="GET"
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout
            ) as response:
                raw_data = response.read().decode("utf-8")
                data = json.loads(raw_data)

        except urllib.error.HTTPError as exc:
            raise NBADataError(
                f"ESPN HTTP error: {exc.code}"
            ) from exc

        except urllib.error.URLError as exc:
            raise NBADataError(
                f"Network error: {exc.reason}"
            ) from exc

        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise NBADataError(
                "Invalid NBA data response."
            ) from exc

        if not isinstance(data, dict):
            raise NBADataError("Unexpected NBA response format.")

        return data

    @staticmethod
    def _get_team(competitors, side):
        for team in competitors:
            if team.get("homeAway") == side:
                details = team.get("team", {})

                return {
                    "id": details.get("id"),
                    "name": details.get("displayName", "Unknown"),
                    "short_name": details.get("shortDisplayName", ""),
                    "abbreviation": details.get("abbreviation", ""),
                    "score": team.get("score"),
                    "winner": team.get("winner", False)
                }

        return {
            "id": None,
            "name": "Unknown",
            "short_name": "",
            "abbreviation": "",
            "score": None,
            "winner": False
        }

    @classmethod
    def _normalize_game(cls, event):
        competitions = event.get("competitions", [])

        if not competitions:
            return None

        competition = competitions[0]
        competitors = competition.get("competitors", [])

        home = cls._get_team(competitors, "home")
        away = cls._get_team(competitors, "away")

        status_data = event.get("status", {})
        status_type = status_data.get("type", {})

        venue_data = competition.get("venue", {})

        return {
            "game_id": event.get("id"),
            "date": event.get("date"),
            "name": event.get("name", ""),
            "short_name": event.get("shortName", ""),

            "home_team": home["name"],
            "home_team_id": home["id"],
            "home_abbreviation": home["abbreviation"],
            "home_score": home["score"],
            "home_winner": home["winner"],

            "away_team": away["name"],
            "away_team_id": away["id"],
            "away_abbreviation": away["abbreviation"],
            "away_score": away["score"],
            "away_winner": away["winner"],

            "status": status_type.get("state", "unknown"),
            "status_detail": status_type.get("shortDetail", ""),
            "status_description": status_type.get("description", ""),
            "period": status_data.get("period"),
            "clock": status_data.get("displayClock"),

            "venue": venue_data.get("fullName", ""),
            "city": venue_data.get("address", {}).get("city", "")
        }

    def get_games(self, match_date):
        """
        Get NBA games for a date.
        Date format: YYYY-MM-DD
        """

        try:
            year, month, day = match_date.split("-")

            if len(year) != 4 or len(month) != 2 or len(day) != 2:
                raise ValueError

            date_value = year + month + day

        except (ValueError, AttributeError):
            raise NBADataError(
                "Date must use YYYY-MM-DD format."
            )

        data = self._request({
            "dates": date_value
        })

        events = data.get("events", [])
        games = []

        for event in events:
            game = self._normalize_game(event)

            if game:
                games.append(game)

        return games

    def get_live_games(self, match_date):
        """
        Return games currently in progress.
        """

        games = self.get_games(match_date)

        return [
            game for game in games
            if game.get("status") == "in"
        ]

    def get_finished_games(self, match_date):
        """
        Return completed games.
        """

        games = self.get_games(match_date)

        return [
            game for game in games
            if game.get("status") == "post"
        ]

    def get_upcoming_games(self, match_date):
        """
        Return games that have not started.
        """

        games = self.get_games(match_date)

        return [
            game for game in games
            if game.get("status") == "pre"
        ]
