"""SQLite persistence for the high-score table."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
import sqlite3

from arcade_reflex.models import GameResult


@dataclass(frozen=True, slots=True)
class ScoreEntry:
    """One row returned from the high-score database."""

    player_name: str
    difficulty: str
    score: int
    hits: int
    misses: int
    accuracy: float
    created_at: str


class HighScoreRepository:
    """Store and retrieve game results using parameterised SQL queries."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def initialise(self) -> None:
        """Create the scores table and index if they do not already exist."""

        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    score INTEGER NOT NULL CHECK (score >= 0),
                    hits INTEGER NOT NULL CHECK (hits >= 0),
                    misses INTEGER NOT NULL CHECK (misses >= 0),
                    accuracy REAL NOT NULL CHECK (accuracy BETWEEN 0 AND 100),
                    duration_seconds REAL NOT NULL CHECK (duration_seconds >= 0),
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_scores_ranking
                    ON scores(score DESC, accuracy DESC, created_at ASC);
                """
            )

    def save_result(self, result: GameResult) -> int:
        """Persist a completed result and return its generated row ID."""

        created_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO scores (
                    player_name,
                    difficulty,
                    score,
                    hits,
                    misses,
                    accuracy,
                    duration_seconds,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.player_name,
                    result.difficulty,
                    result.score,
                    result.hits,
                    result.misses,
                    result.accuracy,
                    result.duration_seconds,
                    created_at,
                ),
            )
            return int(cursor.lastrowid)

    def top_scores(self, limit: int = 10) -> list[ScoreEntry]:
        """Return the highest scores, using accuracy as the tie-breaker."""

        safe_limit = max(1, min(limit, 100))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT player_name, difficulty, score, hits, misses, accuracy, created_at
                FROM scores
                ORDER BY score DESC, accuracy DESC, created_at ASC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [ScoreEntry(**dict(row)) for row in rows]

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Yield a connection and always release the underlying file handle."""

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
