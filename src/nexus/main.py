"""
NEXUS Core - Main Entry Point
The orchestrator: boot sequence, logic gate, agentic loop.
"""

import re
import sys

from nexus.components.boot_manager import BootTracker
from nexus.components import session_memory
from nexus.components import tts
from nexus.components import llm_provider
from nexus.components import vtt
from nexus.config import get_settings

# --- Minimal ANSI styling (no external deps) ---
_RESET = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"


def _style(text: str, *codes: str) -> str:
    return "".join(codes) + text + _RESET


_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

BASE_PROMPT = """
You are NEXUS (Neural Executive Utility System), a local voice assistant.

Voice and tone:
- Speak like a calm mission controller: precise, neutral, quietly confident.
- Never use "Sir", "Master", or honorifics. You are a partner, not a servant.
- Efficient elegance: complete sentences, no filler, no padding, no restating the question.
- Default to 1-3 short sentences. Expand only when the user asks for detail.
- Plain spoken English. No markdown, no bullet lists, no emoji, no code fences
  unless the user explicitly asks for code.

Behavior:
- Answer directly. If you don't know, say so in one line.
- If the request is ambiguous, ask one focused question instead of guessing.
- Match the user's energy: casual when they are casual, transactional when they
  are in a hurry. Drop any wit if the user sounds stressed or rushed.
- Never invent facts, tools, or capabilities you do not have.

Constraints:
- You run locally through Ollama. No internet access.
- You cannot execute shell commands.
- Memory is limited to the current session.

You are NEXUS. Reply in English by default.
"""


def _build_context() -> str:
    memory_context = session_memory.get_context()
    return f"""{BASE_PROMPT}

Conversation History:
{memory_context}

NEXUS:"""


def nexus_run(user_input: str) -> str:
    """Process one user turn: stream the LLM response, speak it sentence by sentence."""
    session_memory.add_message("user", user_input)

    context = _build_context()

    print(_style("NEXUS: ", _BOLD, _CYAN), end="", flush=True)

    buffer = ""
    full_response_parts: list[str] = []

    for line in llm_provider.ask_stream(context, model=get_settings().model):
        if not line:
            continue

        print(line, flush=True)
        full_response_parts.append(line)
        buffer += line + " "

        # Flush complete sentences to TTS as soon as they are ready.
        while True:
            match = _SENTENCE_END.search(buffer)
            if not match:
                break
            sentence = buffer[: match.start()].strip()
            buffer = buffer[match.end():]
            if sentence:
                tts.speak(sentence)

    # Flush any trailing fragment.
    tail = buffer.strip()
    if tail:
        tts.speak(tail)

    print()

    response = " ".join(full_response_parts).strip()
    session_memory.add_message("NEXUS", response)
    return response


def nexus_loop():
    """Main terminal REPL with wake-word gating and silence handling."""
    settings = get_settings()
    wake_word = settings.wake_word
    silence_words = settings.silence_word_list

    print(_style("--- NEXUS v0.1 Operational ---", _BOLD, _CYAN))
    print(_style(f"Say '{wake_word}' to activate. Say 'exit' or 'quit' to shut down.", _DIM))
    print()

    session_memory.load()

    while True:
        try:
            print(_style(f"[idle] waiting for wake word '{wake_word}'...", _DIM))
            wake_text = vtt.wait_for_wake_word(wake_word)

            if not wake_text:
                continue

            print(_style(f"You: {wake_text}", _GREEN))

            # Strip the wake word from the first utterance if it is the only content.
            stripped = wake_text.lower().replace(wake_word.lower(), "").strip(" ,.!?")
            user_input = stripped if stripped else None

            if user_input is None:
                # Wake word alone: listen for the actual request.
                user_input = vtt.listen()
                if not user_input:
                    continue
                print(_style(f"You: {user_input}", _GREEN))

            lowered = user_input.lower().strip(" .!?")

            if lowered in ("exit", "quit"):
                print(_style("NEXUS: Shutting down.", _CYAN))
                session_memory.save()
                break

            if lowered in silence_words:
                print(_style("NEXUS: Standing by.", _CYAN))
                continue

            nexus_run(user_input)

        except (KeyboardInterrupt, EOFError):
            print(_style("\nNEXUS: Shutting down.", _CYAN))
            session_memory.save()
            break
        except Exception as e:
            print(_style(f"NEXUS: Internal error - {e}", _RED))


def pre_warm() -> bool:
    """Verify Ollama is installed and the model is ready before looping."""
    model = get_settings().model

    if not llm_provider.is_ollama_installed():
        print("NEXUS Core: Ollama is not installed. Cannot continue.")
        return False

    try:
        models = llm_provider.list_models()

        if model not in models:
            print("NEXUS Core is missing the neuronal LLM.")
            response = input("Do you want to pull the LLM now? (yes/no): ")

            if response.strip().lower() in ("yes", "y"):
                print(f"Pulling {model}...")
                if not llm_provider.pull_model(model):
                    print(f"Failed to pull {model}.")
                    return False
            else:
                print("NEXUS cannot start without the model.")
                return False

        return True

    except Exception as e:
        print(f"Error pre-warming {model}: {e}")
        return False


def setup():
    """First-run setup process."""
    print("Initializing NEXUS for the first time...")
    print("Checking for Ollama...")

    if llm_provider.is_ollama_installed():
        print("Ollama detected.")
    else:
        print("Ollama not detected. Please install it before continuing.")
        print("Visit: https://ollama.com/download")
        return False

    print("Setup complete.")
    return True


def main():
    boot = BootTracker()
    boot_count = boot.boot()

    if boot_count == 1:
        print("NEXUS is not set up. Setting up now...")
        if not setup():
            print("Setup incomplete. Exiting.")
            return

    print(_style("Welcome back, please wait...", _DIM))
    print(_style("NEXUS Booting...", _BOLD, _CYAN))

    if pre_warm():
        nexus_loop()
    else:
        print("NEXUS failed to boot.")


if __name__ == "__main__":
    main()
