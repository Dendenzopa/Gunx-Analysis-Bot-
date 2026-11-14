import json
import urllib.parse
import urllib.request
import urllib.error
from datetime import date


class APIFootballError(Exception):
    """Custom API error for GUNX."""


class APIFootballClient:
    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self, api_key, timeout=25):
        self.api_key = str(api_key).strip()
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("API Key haijawekwa.")

    def _request(self, endpoint, params=None):
        """Send a GET request to API-Football."""
        params = params or {}

        query = urllib.parse.urlencode(params)
        url = f"{self.BASE_URL}/{endpoint}"

        if query:
            url = f"{url}?{query}"

        request = urllib.request.Request(
            url,
            headers={
                "x-apisports-key": self.api_key
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

        except urllib.error.HTTPError as error:
            if error.code == 401:
                raise APIFootballError(
                    "API Key si sahihi au haijaidhinishwa."
                )

            if error.code == 403:
                raise APIFootballError(
                    "Huduma hii hairuhusiwi kwenye mpango wako."
                )

            if error.code == 429:
                raise APIFootballError(
                    "Umefikia kikomo cha requests. Jaribu baadaye."
                )

            raise APIFootballError(
                f"Hitilafu ya seva: HTTP {error.code}"
            )

        except urllib.error.URLError as error:
            raise APIFootballError(
                f"Imeshindikana kuunganisha na mtandao: {error.reason}"
            )

        except TimeoutError:
            raise APIFootballError(
                "Muda wa kuwasiliana na API umeisha."
            )

        except json.JSONDecodeError:
            raise APIFootballError(
                "Majibu ya API hayajasomeka."
            )

        errors = data.get("errors", {})

        if errors:
            raise APIFootballError(
                f"API imerudisha kosa: {errors}"
            )

        return data

    def get_fixtures(
        self,
        match_date=None,
        league_id=None,
        season=None,
        team_id=None,
        timezone="Africa/Dar_es_Salaam"
    ):
        """
        Get football fixtures for a date.

        Optional filters:
        league_id, season and team_id.
        """
        if match_date is None:
            match_date = date.today().isoformat()

        params = {
            "date": match_date,
            "timezone": timezone
        }

        if league_id is not None:
            params["league"] = int(league_id)

        if season is not None:
            params["season"] = int(season)

        if team_id is not None:
            params["team"] = int(team_id)

        data = self._request("fixtures", params)

        fixtures = []

        for item in data.get("response", []):
            fixture = item.get("fixture", {})
            teams = item.get("teams", {})
            league = item.get("league", {})
            goals = item.get("goals", {})
            status = fixture.get("status", {})

            fixtures.append({
                "fixture_id": fixture.get("id"),
                "date": fixture.get("date"),
                "timestamp": fixture.get("timestamp"),
                "timezone": fixture.get("timezone"),
                "venue": (
                    fixture.get("venue", {}).get("name")
                    if fixture.get("venue") else None
                ),
                "league_id": league.get("id"),
                "league": league.get("name"),
                "country": league.get("country"),
                "season": league.get("season"),
                "round": league.get("round"),
                "home_team": teams.get("home", {}).get("name"),
                "home_team_id": teams.get("home", {}).get("id"),
                "away_team": teams.get("away", {}).get("name"),
                "away_team_id": teams.get("away", {}).get("id"),
                "home_goals": goals.get("home"),
                "away_goals": goals.get("away"),
                "status": status.get("short"),
                "status_long": status.get("long")
            })

        return {
            "results": len(fixtures),
            "fixtures": fixtures,
            "message": (
                "Mechi zimepatikana."
                if fixtures else
                "Hakuna mechi zilizopatikana kwa tarehe hiyo."
            )
        }

    def get_live_fixtures(self):
        """Get currently live football fixtures."""
        data = self._request(
            "fixtures",
            {"live": "all", "timezone": "Africa/Dar_es_Salaam"}
        )

        return data.get("response", [])

    def search_leagues(self, search_text=None, country=None):
        """Search available leagues and cups."""
        params = {}

        if search_text:
            params["search"] = search_text

        if country:
            params["country"] = country

        if not params:
            raise ValueError(
                "Weka jina la ligi au nchi unayotafuta."
            )

        data = self._request("leagues", params)

        leagues = []

        for item in data.get("response", []):
            league = item.get("league", {})
            country_info = item.get("country", {})

            leagues.append({
                "league_id": league.get("id"),
                "league_name": league.get("name"),
                "league_type": league.get("type"),
                "country": country_info.get("name"),
                "seasons": item.get("seasons", [])
            })

        return leagues

    def get_fixture_statistics(self, fixture_id):
        """Get match statistics such as corners and cards."""
        data = self._request(
            "fixtures/statistics",
            {"fixture": int(fixture_id)}
        )

        return data.get("response", [])

    def get_fixture_events(self, fixture_id):
        """Get goals, cards and substitutions."""
        data = self._request(
            "fixtures/events",
            {"fixture": int(fixture_id)}
        )

        return data.get("response", [])

    def get_fixture_predictions(self, fixture_id):
        """Get API-Football predictions for a fixture."""
        data = self._request(
            "predictions",
            {"fixture": int(fixture_id)}
        )

        return data.get("response", [])

    def get_team_statistics(self, league_id, season, team_id):
        """Get team statistics for a particular league and season."""
        params = {
            "league": int(league_id),
            "season": int(season),
            "team": int(team_id)
        }

        data = self._request("teams/statistics", params)

        return data.get("response", {})

    def check_api_status(self):
        """Check API account and subscription information."""
        return self._request("status")
