"""Unit tests for the pure game rules."""

import unittest

from arcade_reflex.game import GameEngine, GameNotRunningError
from arcade_reflex.models import DIFFICULTIES, GameStatus


class FakeClock:
    """Controllable replacement for time.monotonic."""

    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class GameEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.engine = GameEngine(DIFFICULTIES["normal"], clock=self.clock)

    def test_start_requires_a_player_name(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.start("   ")

    def test_start_resets_the_session(self) -> None:
        self.engine.start(" Nour ")

        self.assertEqual(self.engine.player_name, "Nour")
        self.assertEqual(self.engine.status, GameStatus.RUNNING)
        self.assertEqual(self.engine.score, 0)
        self.assertEqual(self.engine.hits, 0)

    def test_hit_increases_score_and_accuracy(self) -> None:
        self.engine.start("Nour")

        points = self.engine.register_hit()

        self.assertEqual(points, 15)
        self.assertEqual(self.engine.score, 15)
        self.assertEqual(self.engine.hits, 1)
        self.assertEqual(self.engine.accuracy, 100.0)

    def test_miss_never_makes_score_negative(self) -> None:
        self.engine.start("Nour")

        penalty = self.engine.register_miss()

        self.assertEqual(penalty, 0)
        self.assertEqual(self.engine.score, 0)
        self.assertEqual(self.engine.misses, 1)
        self.assertEqual(self.engine.accuracy, 0.0)

    def test_time_remaining_uses_the_injected_clock(self) -> None:
        self.engine.start("Nour")
        self.clock.advance(12.25)

        self.assertAlmostEqual(self.engine.time_remaining, 17.75)
        self.assertFalse(self.engine.is_time_up())

    def test_finish_returns_an_immutable_summary(self) -> None:
        self.engine.start("Nour")
        self.engine.register_hit()
        self.engine.register_miss()
        self.clock.advance(8.0)

        result = self.engine.finish()

        self.assertEqual(result.player_name, "Nour")
        self.assertEqual(result.score, 13)
        self.assertEqual(result.hits, 1)
        self.assertEqual(result.misses, 1)
        self.assertEqual(result.accuracy, 50.0)
        self.assertEqual(result.duration_seconds, 8.0)
        self.assertEqual(self.engine.status, GameStatus.FINISHED)
        self.assertIs(self.engine.finish(), result)

    def test_scoring_after_timeout_is_rejected(self) -> None:
        self.engine.start("Nour")
        self.clock.advance(31)

        with self.assertRaises(GameNotRunningError):
            self.engine.register_hit()

        self.assertEqual(self.engine.status, GameStatus.FINISHED)


if __name__ == "__main__":
    unittest.main()

