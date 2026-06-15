"""
LLM Provider
Wraps calls to a local Ollama model.
"""

import subprocess

DEFAULT_MODEL = "ministral-3"
TIMEOUT_SECONDS = 120


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


def is_model_available(model: str) -> bool:
    """Check whether `model` is present in `ollama list` output."""
    try:
        return model in list_models()
    except subprocess.CalledProcessError:
        return False


def pull_model(model: str) -> bool:
    """Pull `model` via ollama. Returns True on success."""
    try:
        subprocess.run(["ollama", "pull", model], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def ask(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Send `prompt` to the local model and return the response text."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: LLM request timed out."
    except subprocess.CalledProcessError as e:
        return f"Error calling Ollama: {e.stderr.strip()}"
    except FileNotFoundError:
        return "Error: Ollama is not installed or not on PATH."
