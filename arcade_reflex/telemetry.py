"""Local JSON Lines telemetry for studying product instrumentation."""

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any


class TelemetryLogger:
    """Append structured game events to a local JSONL file."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: str, **properties: Any) -> None:
        """Write one timestamped event with JSON-serialisable properties."""

        cleaned_event = event.strip()
        if not cleaned_event:
            raise ValueError("Telemetry event name cannot be empty.")

        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": cleaned_event,
            "properties": properties,
        }
        with self.output_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, sort_keys=True) + "\n")

    def read_events(self) -> list[dict[str, Any]]:
        """Read all valid events; useful for tests and local debugging."""

        if not self.output_path.exists():
            return []
        with self.output_path.open("r", encoding="utf-8") as stream:
            return [json.loads(line) for line in stream if line.strip()]

