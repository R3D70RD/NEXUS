"""
Session Memory
Holds short-term conversation history in memory, with optional
persistence to disk between runs.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "session_history.json")

MAX_HISTORY = 10

_conversation_history = []


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def add_message(role: str, content: str):
    """Append a message to the in-memory conversation history."""
    _conversation_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })

    if len(_conversation_history) > MAX_HISTORY:
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


def save():
    """Persist the current session history to disk."""
    _ensure_data_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(_conversation_history, f, indent=4)


def load():
    """Load session history from disk, if present."""
    global _conversation_history

    if not os.path.exists(HISTORY_FILE):
        return

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                _conversation_history = data[-MAX_HISTORY:]
    except (json.JSONDecodeError, OSError):
        pass
