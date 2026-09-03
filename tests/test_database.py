"""Integration tests for the SQLite score repository."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from arcade_reflex.database import HighScoreRepository
from arcade_reflex.models import GameResult


def make_result(player: str, score: int, accuracy: float) -> GameResult:
    return GameResult(
        player_name=player,
        difficulty="Normal",
        score=score,
        hits=8,
        misses=2,
        accuracy=accuracy,
        duration_seconds=30.0,
    )


class HighScoreRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "scores.db"
        self.repository = HighScoreRepository(database_path)
        self.repository.initialise()

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_scores_are_ordered_by_score_then_accuracy(self) -> None:
        self.repository.save_result(make_result("Sam", 80, 70.0))
        self.repository.save_result(make_result("Nour", 120, 75.0))
        self.repository.save_result(make_result("Alex", 120, 90.0))

        scores = self.repository.top_scores()

        self.assertEqual([score.player_name for score in scores], ["Alex", "Nour", "Sam"])

    def test_limit_is_applied(self) -> None:
        for number in range(5):
            self.repository.save_result(make_result(f"Player {number}", number * 10, 80.0))

        scores = self.repository.top_scores(limit=2)

        self.assertEqual(len(scores), 2)
        self.assertEqual(scores[0].score, 40)

    def test_player_name_is_stored_with_parameterised_sql(self) -> None:
        unusual_name = "Nour'); DROP TABLE scores;--"
        self.repository.save_result(make_result(unusual_name, 50, 50.0))

        scores = self.repository.top_scores()

        self.assertEqual(scores[0].player_name, unusual_name)
        self.repository.save_result(make_result("Still works", 60, 60.0))
        self.assertEqual(len(self.repository.top_scores()), 2)


if __name__ == "__main__":
    unittest.main()

