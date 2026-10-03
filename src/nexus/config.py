"""Runtime settings and on-disk paths for NEXUS."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR = PACKAGE_DIR / "data"

_INT_FIELDS = {
    "listen_duration_seconds",
    "sample_rate",
    "max_history",
    "llm_timeout_seconds",
}


@dataclass
class Settings:
    model: str = "ministral-3"
    whisper_model: str = "small"
    listen_duration_seconds: int = 5
    sample_rate: int = 16000
    max_history: int = 10
    voice_filename: str = "en_US-ljspeech-high.onnx"
    llm_timeout_seconds: int = 120
    data_dir: Path = DATA_DIR

    @property
    def settings_file(self) -> Path:
        return self.data_dir / "settings.json"

    @property
    def voice_model_path(self) -> Path:
        return self.data_dir / "voices" / self.voice_filename

    @property
    def history_file(self) -> Path:
        return self.data_dir / "session_history.json"

    @property
    def boot_state_file(self) -> Path:
        return self.data_dir / "boot_state.json"

    @property
    def live_input_wav(self) -> Path:
        return self.data_dir / "input" / "live_input.wav"


_settings = Settings()


def get_settings() -> Settings:
    """Return the process-wide settings object."""
    return _settings


def load_settings(path: Path | None = None, *, data_dir: Path | None = None) -> Settings:
    """Load settings from JSON if present; otherwise keep defaults."""
    global _settings

    settings = Settings()
    if data_dir is not None:
        settings.data_dir = Path(data_dir)

    settings_path = Path(path) if path is not None else settings.settings_file
    if settings_path.exists():
        try:
            raw = json.loads(settings_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            raw = {}
        if isinstance(raw, dict):
            allowed = {item.name for item in fields(Settings)} - {"data_dir"}
            for key, value in raw.items():
                if key not in allowed:
                    continue
                if key in _INT_FIELDS:
                    try:
                        value = int(value)
                    except (TypeError, ValueError):
                        continue
                setattr(settings, key, value)

    _settings = settings
    return _settings


def save_settings(path: Path | None = None) -> None:
    """Persist the current settings (excluding data_dir) to JSON."""
    settings = get_settings()
    dest = Path(path) if path is not None else settings.settings_file
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(settings)
    payload.pop("data_dir", None)
    dest.write_text(json.dumps(payload, indent=4), encoding="utf-8")


load_settings()
