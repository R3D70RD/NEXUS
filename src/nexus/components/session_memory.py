"""
Session Memory
Holds short-term conversation history in memory, with optional
persistence to disk between runs.
"""

from __future__ import annotations

import json
import os
from datetime import datetime

from nexus.config import get_settings

_conversation_history = []


def _history_file() -> str:
    return str(get_settings().history_file)


def _max_history() -> int:
    return get_settings().max_history


def _ensure_data_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def add_message(role: str, content: str):
    """Append a message to the in-memory conversation history."""
    _conversation_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    limit = _max_history()
    while len(_conversation_history) > limit:
        _conversation_history.pop(0)


def get_context() -> str:
    """Return the conversation history formatted for prompt injection."""
    formatted = ""

    for msg in _conversation_history:
        formatted += f"{msg['role'].capitalize()}: {msg['content']}\n"

    return formatted


def get_history() -> list:
    """Return the raw conversation history list."""
    return list(_conversation_history)


def clear():
    """Clear the in-memory conversation history."""
    _conversation_history.clear()


def save(path: str | None = None):
    """Persist the current session history to disk."""
    history_file = path or _history_file()
    _ensure_data_dir(history_file)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(_conversation_history, f, indent=4)


def load(path: str | None = None):
    """Load session history from disk, if present."""
    global _conversation_history

    history_file = path or _history_file()
    if not os.path.exists(history_file):
        return

    try:
        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                _conversation_history = data[-_max_history():]
    except (json.JSONDecodeError, OSError):
        pass
