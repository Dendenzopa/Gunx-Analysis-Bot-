

# GUNX ANALYSIS BOT

### Global Football Match Analysis System

GUNX ANALYSIS BOT is an Android football analysis application designed to retrieve football fixtures and calculate match probability estimates.

## Main Features

- Retrieve football fixtures using API-Football.
- Search matches by date.
- Display teams, leagues, countries and kickoff times.
- Calculate 1X2 probabilities.
- Calculate Double Chance probabilities.
- Analyze GG / NG.
- Analyze Over / Under 1.5, 2.5 and 3.5.
- Estimate the most likely score.
- Display expected goals.
- Display model risk assessment.

## Project Structure

```text
Gunx-Analysis-Bot/
│
├── main.py
├── gui_app.py
├── analyzer.py
├── markets.py
├── api.py
├── buildozer.spec
├── README.md
│
└── .github/
    └── workflows/
        └── build.yml
```

## Requirements

- Python 3.10
- Kivy
- Buildozer
- Android SDK and NDK
- API-Football API key

## API Configuration

GUNX uses API-Football:

https://v3.football.api-sports.io

To use the application:

1. Create an API-Football account.
2. Obtain your API key.
3. Open GUNX ANALYSIS BOT.
4. Enter your API key.
5. Select a match date.
6. Retrieve available fixtures.

Never publish your private API key in this repository.

## Running the Application

Install dependencies:

```bash
pip install kivy
```

Run:

```bash
python main.py
```

## Building Android APK

The project uses Buildozer and GitHub Actions.

1. Open the GitHub repository.
2. Select Actions.
3. Select GUNX ANALYSIS BOT APK BUILD.
4. Select Run workflow.
5. Wait for the build to finish.
6. Download the APK from the workflow Artifacts.

## Analysis Method

The current analysis engine uses the Poisson probability model.

It uses expected goals for both teams to estimate:

- Home win
- Draw
- Away win
- Both Teams To Score
- Over and Under goal markets
- Most likely score

## Current Limitations

- Expected goals are currently entered manually.
- Live fixture retrieval depends on API access.
- Corners and cards require additional statistics.
- HT/FT requires first-half data.
- API data availability depends on competition and subscription.
- The application does not guarantee betting outcomes.

## Disclaimer

GUNX ANALYSIS BOT provides statistical estimates for informational purposes only.

Predictions are not guaranteed results. Always consider uncertainty and risk before making betting decisions.

---

GUNX ANALYSIS BOT  
The Pulse of Global Football Analysis.
