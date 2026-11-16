import json
import urllib.parse
import urllib.request
import urllib.error
import socket
import ssl
import certifi

from datetime import datetime, timezone, timedelta


class APIFootballError(Exception):
    """Custom API error for GUNX."""


class APIFootballClient:

    BASE_URL = "https://v3.football.api-sports.io"

    TANZANIA_TZ = timezone(timedelta(hours=3))

    def __init__(self, api_key, timeout=25):

        self.api_key = str(api_key or "").strip()
        self.timeout = int(timeout)

        if not self.api_key:
            raise ValueError("API Key haijawekwa.")

        if self.timeout < 1:
            raise ValueError("Timeout lazima iwe zaidi ya sifuri.")

    def _request(self, endpoint, params=None):

        params = params or {}
        endpoint = str(endpoint).strip("/")

        query = urllib.parse.urlencode(params)

        url = f"{self.BASE_URL}/{endpoint}"

        if query:
            url = f"{url}?{query}"

        request = urllib.request.Request(
            url,
            headers={
                "x-apisports-key": self.api_key,
                "Accept": "application/json",
                "User-Agent": "GUNX-ANALYSIS-BOT/1.0"
            },
            method="GET"
        )

        try:

            ssl_context = ssl.create_default_context(
                cafile=certifi.where()
            )

            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
                context=ssl_context
            ) as response:

                raw_data = response.read().decode("utf-8")

            data = json.loads(raw_data)

        except urllib.error.HTTPError as error:

            error_body = ""

            try:
                error_body = error.read().decode(
                    "utf-8", errors="replace"
                )
            except Exception:
                pass

            if error.code == 401:
                raise APIFootballError(
                    "API Key si sahihi au haijaidhinishwa."
                )

            if error.code == 403:
                raise APIFootballError(
                    "Huduma hii hairuhusiwi kwenye mpango wako wa API."
                )

            if error.code == 404:
                raise APIFootballError(
                    "Endpoint au taarifa uliyoomba haijapatikana."
                )

            if error.code == 429:
                raise APIFootballError(
                    "Umefikia kikomo cha requests. Jaribu baadaye."
                )

            raise APIFootballError(
                f"HTTP Error {error.code}: {error_body[:300]}"
            )

        except urllib.error.URLError as error:

            reason = getattr(error, "reason", error)

            if isinstance(reason, (socket.timeout, TimeoutError)):
                raise APIFootballError(
                    "Muda wa kuwasiliana na API umeisha."
                )

            if isinstance(reason, ssl.SSLError):
                raise APIFootballError(
                    f"SSL Certificate Error: {reason}"
                )

            raise APIFootballError(
                f"Hitilafu ya mtandao: {reason}"
            )

        except ssl.SSLError as error:

            raise APIFootballError(
                f"SSL Certificate Error: {error}"
            )

        except (socket.timeout, TimeoutError):

            raise APIFootballError(
                "Muda wa kuwasiliana na API umeisha."
            )

        except (ConnectionError, OSError) as error:

            raise APIFootballError(
                f"Imeshindikana kuunganisha: {error}"
            )

        except json.JSONDecodeError:

            raise APIFootballError(
                "Majibu ya API si JSON halali."
            )

        if not isinstance(data, dict):
            raise APIFootballError(
                "Muundo wa majibu ya API si sahihi."
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
        timezone_name="Africa/Dar_es_Salaam"
    ):

        if match_date is None:
            match_date = datetime.now(
                self.TANZANIA_TZ
            ).date().isoformat()

        params = {
            "date": str(match_date),
            "timezone": timezone_name
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

            fixture = item.get("fixture") or {}
            teams = item.get("teams") or {}
            league = item.get("league") or {}
            goals = item.get("goals") or {}
            status = fixture.get("status") or {}
            venue = fixture.get("venue") or {}

            home = teams.get("home") or {}
            away = teams.get("away") or {}

            fixtures.append({

                "fixture_id": fixture.get("id"),
                "date": fixture.get("date"),
                "timestamp": fixture.get("timestamp"),
                "timezone": fixture.get("timezone"),
                "venue": venue.get("name"),

                "league_id": league.get("id"),
                "league": league.get("name"),
                "country": league.get("country"),
                "season": league.get("season"),
                "round": league.get("round"),

                "home_team": home.get("name"),
                "home_team_id": home.get("id"),

                "away_team": away.get("name"),
                "away_team_id": away.get("id"),

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

        data = self._request(
            "fixtures",
            {
                "live": "all",
                "timezone": "Africa/Dar_es_Salaam"
            }
        )

        return data.get("response", [])

    def search_leagues(self, search_text=None, country=None):

        params = {}

        if search_text:
            params["search"] = str(search_text).strip()

        if country:
            params["country"] = str(country).strip()

        if not params:
            raise ValueError(
                "Weka jina la ligi au nchi unayotafuta."
            )

        data = self._request("leagues", params)

        leagues = []

        for item in data.get("response", []):

            league = item.get("league") or {}
            country_info = item.get("country") or {}

            leagues.append({

                "league_id": league.get("id"),
                "league_name": league.get("name"),
                "league_type": league.get("type"),
                "country": country_info.get("name"),
                "seasons": item.get("seasons", [])

            })

        return leagues

    def get_fixture_statistics(self, fixture_id):

        data = self._request(
            "fixtures/statistics",
            {"fixture": int(fixture_id)}
        )

        return data.get("response", [])

    def get_fixture_events(self, fixture_id):

        data = self._request(
            "fixtures/events",
            {"fixture": int(fixture_id)}
        )

        return data.get("response", [])

    def get_fixture_predictions(self, fixture_id):

        data = self._request(
            "predictions",
            {"fixture": int(fixture_id)}
        )

        return data.get("response", [])

    def get_team_statistics(
        self,
        league_id,
        season,
        team_id
    ):

        params = {
            "league": int(league_id),
            "season": int(season),
            "team": int(team_id)
        }

        data = self._request(
            "teams/statistics",
            params
        )

        return data.get("response", {})

    def get_fixture_odds(self, fixture_id):

        data = self._request(
            "odds",
            {"fixture": int(fixture_id)}
        )

        return data.get("response", [])

    def check_api_status(self):

        return self._request("status")

    def test_connection(self):

        try:
            data = self.check_api_status()
            response = data.get("response", {})

            account = response.get("account", {})
            subscription = response.get("subscription", {})
            requests_info = response.get("requests", {})

            return {
                "success": True,
                "message": "GUNX API connection successful.",
                "account": account,
                "subscription": subscription,
                "requests": requests_info,
            }

        except APIFootballError as error:
            return {
                "success": False,
                "message": str(error),
            }
