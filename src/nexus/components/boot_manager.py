"""
Boot Manager
Tracks boot count and first-run state via a JSON file.
"""

from __future__ import annotations

import json
import os

from nexus.config import get_settings


def _default_boot_file() -> str:
    return str(get_settings().boot_state_file)


class BootTracker:
    """Tracks how many times NEXUS has booted, persisted to disk."""

    def __init__(self, path: str | None = None):
        self.path = path or _default_boot_file()
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def _read_state(self) -> dict:
        if not os.path.exists(self.path):
            return {"counter": 0}

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "counter" not in data:
                    data["counter"] = 0
                return data
        except (json.JSONDecodeError, OSError):
            return {"counter": 0}

    def _write_state(self, data: dict):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def boot(self) -> int:
        """Increment and persist the boot counter. Returns the new count."""
        state = self._read_state()
        state["counter"] += 1
        self._write_state(state)
        return state["counter"]

    def get_count(self) -> int:
        """Return the current boot count without incrementing it."""
        return self._read_state().get("counter", 0)

    def reset(self):
        """Reset the boot counter to zero."""
        self._write_state({"counter": 0})
