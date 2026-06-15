"""
Boot Manager
Tracks boot count and first-run state via a JSON file.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BOOT_FILE = os.path.join(DATA_DIR, "boot_state.json")


class BootTracker:
    """Tracks how many times NEXUS has booted, persisted to disk."""

    def __init__(self, path: str = BOOT_FILE):
        self.path = path
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
