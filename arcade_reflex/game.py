"""Pure game rules, independent of the graphical interface."""

from collections.abc import Callable
from time import monotonic

from arcade_reflex.models import Difficulty, GameResult, GameStatus


class GameNotRunningError(RuntimeError):
    """Raised when a scoring action is attempted outside an active game."""


class GameEngine:
    """Manage scoring and timing for one ArcadeReflex session.

    The class accepts a clock function so tests can control time without
    sleeping. Keeping these rules outside Tkinter also makes the code easier
    to reuse in a web, mobile or cabinet interface later.
    """

    def __init__(
        self,
        difficulty: Difficulty,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.difficulty = difficulty
        self._clock = clock
        self._status = GameStatus.IDLE
        self._player_name = ""
        self._score = 0
        self._hits = 0
        self._misses = 0
        self._started_at: float | None = None
        self._finished_result: GameResult | None = None

    @property
    def status(self) -> GameStatus:
        return self._status

    @property
    def player_name(self) -> str:
        return self._player_name

    @property
    def score(self) -> int:
        return self._score

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def accuracy(self) -> float:
        attempts = self._hits + self._misses
        if attempts == 0:
            return 0.0
        return round((self._hits / attempts) * 100, 1)

    @property
    def elapsed_seconds(self) -> float:
        if self._started_at is None:
            return 0.0
        elapsed = max(0.0, self._clock() - self._started_at)
        return min(elapsed, float(self.difficulty.duration_seconds))

    @property
    def time_remaining(self) -> float:
        remaining = self.difficulty.duration_seconds - self.elapsed_seconds
        return max(0.0, remaining)

    def start(self, player_name: str) -> None:
        """Reset and start a session for a non-empty player name."""

        cleaned_name = player_name.strip()
        if not cleaned_name:
            raise ValueError("Player name cannot be empty.")

        self._player_name = cleaned_name[:30]
        self._score = 0
        self._hits = 0
        self._misses = 0
        self._started_at = self._clock()
        self._finished_result = None
        self._status = GameStatus.RUNNING

    def register_hit(self) -> int:
        """Record a successful target press and return the score increase."""

        self._ensure_running()
        self._hits += 1
        self._score += self.difficulty.points_per_hit
        return self.difficulty.points_per_hit

    def register_miss(self) -> int:
        """Record an expired target and return the score decrease."""

        self._ensure_running()
        self._misses += 1
        previous_score = self._score
        self._score = max(0, self._score - self.difficulty.miss_penalty)
        return previous_score - self._score

    def is_time_up(self) -> bool:
        """Return whether an active session has used its full duration."""

        return self._status is GameStatus.RUNNING and self.time_remaining <= 0

    def finish(self) -> GameResult:
        """Finish the session and return the same immutable result thereafter."""

        if self._finished_result is not None:
            return self._finished_result
        if self._status is GameStatus.IDLE or self._started_at is None:
            raise GameNotRunningError("Start the game before finishing it.")

        result = GameResult(
            player_name=self._player_name,
            difficulty=self.difficulty.name,
            score=self._score,
            hits=self._hits,
            misses=self._misses,
            accuracy=self.accuracy,
            duration_seconds=round(self.elapsed_seconds, 2),
        )
        self._finished_result = result
        self._status = GameStatus.FINISHED
        return result

    def _ensure_running(self) -> None:
        if self._status is not GameStatus.RUNNING:
            raise GameNotRunningError("The game is not running.")
        if self.is_time_up():
            self.finish()
            raise GameNotRunningError("The game timer has finished.")

