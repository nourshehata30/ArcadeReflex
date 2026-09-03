"""Shared domain models for ArcadeReflex."""

from dataclasses import dataclass
from enum import Enum


class GameStatus(str, Enum):
    """Possible lifecycle states for one game session."""

    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"


@dataclass(frozen=True, slots=True)
class Difficulty:
    """Configuration values that control a game session."""

    name: str
    duration_seconds: int
    target_interval_ms: int
    points_per_hit: int
    miss_penalty: int


DIFFICULTIES: dict[str, Difficulty] = {
    "easy": Difficulty(
        name="Easy",
        duration_seconds=30,
        target_interval_ms=1_500,
        points_per_hit=10,
        miss_penalty=1,
    ),
    "normal": Difficulty(
        name="Normal",
        duration_seconds=30,
        target_interval_ms=1_050,
        points_per_hit=15,
        miss_penalty=2,
    ),
    "hard": Difficulty(
        name="Hard",
        duration_seconds=30,
        target_interval_ms=700,
        points_per_hit=20,
        miss_penalty=3,
    ),
}


@dataclass(frozen=True, slots=True)
class GameResult:
    """Immutable summary produced when a game session finishes."""

    player_name: str
    difficulty: str
    score: int
    hits: int
    misses: int
    accuracy: float
    duration_seconds: float

