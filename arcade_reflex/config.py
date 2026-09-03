"""Application paths and visual constants."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "arcade_reflex.db"
TELEMETRY_PATH = DATA_DIR / "telemetry.jsonl"

WINDOW_TITLE = "ArcadeReflex"
WINDOW_SIZE = "980x700"

COLOURS = {
    "background": "#0B1020",
    "panel": "#151D33",
    "text": "#F7F9FC",
    "muted": "#AAB5CC",
    "accent": "#35D0BA",
    "accent_hover": "#6BE7D4",
    "target": "#FF4D6D",
    "target_active": "#FF8FA3",
    "warning": "#FFD166",
}

