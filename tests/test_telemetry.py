"""Unit tests for local telemetry logging."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from arcade_reflex.telemetry import TelemetryLogger


class TelemetryLoggerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.path = Path(self.temp_directory.name) / "events.jsonl"
        self.logger = TelemetryLogger(self.path)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_log_appends_structured_events(self) -> None:
        self.logger.log("session_started", player="Nour", difficulty="Normal")
        self.logger.log("target_hit", score=15)

        events = self.logger.read_events()

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "session_started")
        self.assertEqual(events[0]["properties"]["player"], "Nour")
        self.assertIn("timestamp", events[0])
        self.assertEqual(events[1]["properties"]["score"], 15)

    def test_empty_event_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.logger.log("   ")

    def test_reading_before_any_event_returns_an_empty_list(self) -> None:
        self.assertEqual(self.logger.read_events(), [])


if __name__ == "__main__":
    unittest.main()

