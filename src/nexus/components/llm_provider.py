"""
LLM Provider
Wraps calls to a local Ollama model.
"""

from __future__ import annotations

import subprocess

from nexus.config import get_settings


def _model_name(model: str | None = None) -> str:
    return model or get_settings().model


def _timeout_seconds() -> int:
    return get_settings().llm_timeout_seconds


def is_ollama_installed() -> bool:
    """Check whether the `ollama` CLI is available."""
    try:
        subprocess.run(
            ["ollama", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def list_models() -> str:
    """Return the raw output of `ollama list`."""
    result = subprocess.run(
        ["ollama", "list"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip()


def is_model_available(model: str | None = None) -> bool:
    """Check whether `model` is present in `ollama list` output."""
    try:
        return _model_name(model) in list_models()
    except subprocess.CalledProcessError:
        return False


def pull_model(model: str | None = None) -> bool:
    """Pull `model` via ollama. Returns True on success."""
    try:
        subprocess.run(["ollama", "pull", _model_name(model)], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def ask(prompt: str, model: str | None = None) -> str:
    """Send `prompt` to the local model and return the response text."""
    try:
        result = subprocess.run(
            ["ollama", "run", _model_name(model), prompt],
            capture_output=True,
            text=True,
            timeout=_timeout_seconds(),
            check=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: LLM request timed out."
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        return f"Error calling Ollama: {stderr}"
    except FileNotFoundError:
        return "Error: Ollama is not installed or not on PATH."
