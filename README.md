# ArcadeReflex

ArcadeReflex is a touchscreen-style reaction game built with Python's standard library. Large controls make it suitable as an arcade-cabinet prototype: the player taps a moving target before it expires, earns points for hits, loses points for misses, and competes on a persistent local leaderboard.

The project demonstrates user-interface development, clean separation of responsibilities, automated testing, SQLite persistence, telemetry and end-to-end software delivery.

## Features

- Large-button Tkinter interface designed with touchscreen use in mind.
- Three difficulty levels with different target speeds and scoring rules.
- Pure, reusable game engine separated from the graphical interface.
- SQLite leaderboard with parameterised queries and deterministic ranking.
- JSON Lines telemetry for session, hit, miss and completion events.
- Automated unit and integration tests using `unittest`.
- Type hints, dataclasses, docstrings and no third-party dependencies.

## Run the project

Use Python 3.11 or newer. From the `ArcadeReflex` directory:

```powershell
python main.py
```

On Windows, `py main.py` also works.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

The tests do not open the graphical interface. They verify the game rules, timing, scoring, database ranking, SQL safety and telemetry format.

## Architecture

```text
ArcadeReflex/
|-- main.py                    # Small application entry point
|-- arcade_reflex/
|   |-- models.py              # Dataclasses, game state and difficulties
|   |-- game.py                # Pure timing and scoring rules
|   |-- database.py            # SQLite high-score repository
|   |-- telemetry.py           # Structured JSONL event logging
|   `-- ui.py                  # Tkinter views and event coordination
|-- tests/                     # Automated unit and integration tests
`-- data/                      # Runtime database and telemetry files
```

The UI depends on the game engine and services, but the game engine does not depend on Tkinter, SQLite or files. This direction of dependency keeps the important rules easy to test and allows another interface to reuse them later.

## Data flow

1. The UI validates the player's name and selected difficulty.
2. `GameEngine` starts a timed session and owns scoring rules.
3. UI events call `register_hit()` or `register_miss()`.
4. `TelemetryLogger` records structured events for product analysis.
5. When time expires, the engine creates an immutable `GameResult`.
6. `HighScoreRepository` saves the result and reloads the leaderboard.

## Quality and security choices

- All SQL values use placeholders, which prevents player names being interpreted as SQL.
- Scores and accuracy have database constraints.
- The score never becomes negative.
- The player name is validated, trimmed and length-limited.
- Time is injected into `GameEngine`, so timing tests run instantly and deterministically.
- Generated database and telemetry files are excluded from Git.

