
import json
import urllib.parse
import urllib.request
import urllib.error


class BasketballAPIError(Exception):
    """Custom error for GUNX Basketball API."""


class BasketballAPIClient:
    BASE_URL = "https://v1.basketball.api-sports.io"

    def __init__(self, api_key, timeout=25):
        self.api_key = str(api_key).strip()
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("API key is required.")

    def _request(self, endpoint, params=None):
        params = params or {}

        query = urllib.parse.urlencode({
            key: value for key, value in params.items()
            if value is not None
        })

        url = f"{self.BASE_URL}/{endpoint}"

        if query:
            url += f"?{query}"

        request = urllib.request.Request(
            url,
            headers={
                "x-apisports-key": self.api_key,
                "Accept": "application/json",
            },
            method="GET"
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout
            ) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as exc:
            raise BasketballAPIError(
                f"Basketball HTTP error: {exc.code}"
            ) from exc

        except urllib.error.URLError as exc:
            raise BasketballAPIError(
                f"Network connection failed: {exc.reason}"
            ) from exc

        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise BasketballAPIError(
                "Invalid response from Basketball API."
            ) from exc

        errors = data.get("errors")

        if errors:
            raise BasketballAPIError(
                f"Basketball API rejected request: {errors}"
            )

        return data

    def check_access(self):
        """Check whether the account can access API-Basketball."""
        data = self._request("status")
        return {
            "connected": True,
            "message": "Basketball API connection successful.",
            "data": data
        }

    def get_games(self, match_date, timezone_name="Africa/Dar_es_Salaam"):
        """Retrieve basketball games for a selected date."""
        data = self._request(
            "games",
            {
                "date": match_date,
                "timezone": timezone_name
            }
        )

        return data.get("response", [])

    def get_team_statistics(
        self,
        league_id,
        season,
        team_id,
        match_date=None
    ):
        """Retrieve statistics for a basketball team."""
        data = self._request(
            "statistics",
            {
                "league": league_id,
                "season": season,
                "team": team_id,
                "date": match_date
            }
        )

        return data.get("response", {})

    def get_odds(self, game_id):
        """Retrieve available pre-match odds for a game."""
        data = self._request(
            "odds",
            {
                "game": game_id
            }
        )

        return data.get("response", [])
