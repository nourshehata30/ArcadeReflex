# ArcadeReflex Interview Guide

Do not memorise lines without understanding them. Run the game, change one rule, break a test, fix it, and then practise explaining the project in your own words.

## 30-second explanation

"I built ArcadeReflex, a touchscreen-style reaction game in Python. I separated the timing and scoring rules from the Tkinter interface so the core logic is easy to test and could later be reused by another front end. Completed games are stored in SQLite, and structured JSONL telemetry records player events. I added automated tests around the game engine, database ranking and telemetry, using an injected clock so timing tests are fast and deterministic."

## Why this project fits the role

- **Gaming product:** it is a playable arcade prototype rather than a static website.
- **Clean, maintainable code:** UI, rules, storage and telemetry live in separate modules.
- **Testing:** the most important logic runs without the GUI and has automated tests.
- **End-to-end development:** input, game rules, interface, persistence, telemetry and documentation are included.
- **Team readiness:** module boundaries make ownership and code review easier.
- **Growth potential:** the Python engine could be replaced with C++ or exposed through an API.

## Explain each module

### `models.py`

Defines stable data structures. `Difficulty` holds configuration instead of scattering numbers throughout the code. `GameResult` is frozen so a completed score cannot be changed accidentally.

### `game.py`

Owns timing and scoring rules. It has no Tkinter or database imports, which makes it portable and easy to test. A clock function is injected rather than calling real time directly in every method.

### `ui.py`

Builds the touchscreen-style interface and coordinates user events. Tkinter's `after()` schedules target movement and timer updates without blocking the event loop.

### `database.py`

Implements the repository pattern: the UI asks for scores without knowing the SQL details. Queries are parameterised, database constraints reject invalid values, and ranking is explicit.

### `telemetry.py`

Writes one JSON object per line. JSONL is simple to inspect and can be streamed into a future cloud analytics service.

## Questions you should be ready for

### Why Python instead of C++ or Java?

Python let me deliver and test the complete product quickly using standard-library tools. I kept the core engine independent of the interface so a future version could move performance-sensitive rules into C++ or reimplement the UI in Java without redesigning the whole system.

### What does "clean architecture" mean here?

The business rules do not know about buttons, SQL or files. Dependencies point from the UI towards the game engine, so the rules remain simple, testable and reusable.

### How did you test time-based behaviour?

`GameEngine` accepts a clock callable. Tests use `FakeClock`, advance it instantly and assert the remaining time or finished state. This avoids slow, unreliable `sleep()` calls.

### Why SQLite?

It is built into Python, requires no server and is appropriate for a single cabinet prototype. If multiple cabinets needed a shared leaderboard, I would put a REST API in front of a managed database.

### What is telemetry, and why include it?

Telemetry is structured operational or usage data. The events can show session starts, hits, misses, completion, difficulty and accuracy, helping the team tune game balance and spot abandoned sessions.

### How is SQL injection prevented?

The repository uses `?` placeholders and passes values separately. A test stores a player name containing SQL syntax and proves the scores table still works.

### What bug did your tests catch?

The first database tests passed their assertions but failed during cleanup on Windows because SQLite's built-in context manager commits or rolls back without closing the connection. I replaced it with a small `contextmanager` that commits on success, rolls back on failure and always closes the connection in `finally`. This removed the locked-file error and made resource ownership explicit.

### What would you improve next?

1. Add sound, animation and sprite assets.
2. Add a REST API and cloud leaderboard.
3. Package the app for a cabinet and add hardware-button input.
4. Introduce a C++ scoring engine through Python bindings.
5. Add continuous integration to run tests on every pull request.
6. Add difficulty balancing based on telemetry.

## Practical study tasks

Complete these yourself before the interview:

1. Run all tests and explain what each one protects.
2. Change Normal mode from 30 to 20 seconds and update one test.
3. Add a fourth `Expert` difficulty.
4. Add a new telemetry property called `attempts` to the finished event.
5. Change leaderboard ordering and explain the SQL `ORDER BY` clause.
6. Draw the module dependency diagram on paper.
7. Make one small Git commit for each change with a clear message.

## STAR example

**Situation:** I wanted a portfolio project that demonstrated more than a user interface.

**Task:** I designed a complete, testable arcade prototype with persistent scores and product telemetry.

**Action:** I separated the game rules from Tkinter, injected the clock for deterministic tests, used parameterised SQLite queries, and logged structured events.

**Result:** I produced a working, dependency-free project with automated coverage of the key rules and a clear path to C++, cloud and cabinet integration.
