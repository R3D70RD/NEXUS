# NEXUS - Architecture

## Overview

NEXUS Core is the orchestrator and entry point for Phase 1: a
local-first, modular assistant on Ollama, with session memory,
voice I/O, and a structured boot sequence.

The installable Python package is `nexus` (not `ai_infrastructure`).
Run it with `nexus` or `python -m nexus` after `pip install -e .`.

## Module Map

```
src/nexus/
├── __main__.py                 # python -m nexus
├── main.py                     # Boot sequence, logic gate, agentic loop
├── config.py                   # Defaults + optional data/settings.json
├── components/
│   ├── boot_manager.py         # First-run detection, persistent boot counter
│   ├── session_memory.py       # Short-term conversation history
│   ├── llm_provider.py         # Ollama CLI wrapper
│   ├── vtt.py                  # Whisper speech-to-text
│   └── tts.py                  # Piper TTS with silent fallback
└── data/                       # Runtime only (gitignored)
    ├── settings.json           # Optional overrides
    ├── boot_state.json
    ├── session_history.json
    ├── input/live_input.wav
    └── voices/                 # Piper voice models
```

## Boot Sequence

1. `BootTracker.boot()` increments the persisted boot counter.
2. If this is boot #1, `setup()` runs (checks Ollama is installed).
3. `pre_warm()` verifies Ollama is installed and the configured model
   (`ministral-3` by default) is available, offering to pull it if not.
4. `nexus_loop()` starts the voice REPL, loading any saved session
   history from disk.

## Logic Gate

`nexus_run()` is the core gate: every user turn is appended to session
memory, the full conversation context is assembled with `BASE_PROMPT`,
sent to the local LLM via `llm_provider.ask()`, and the response is
stored back into memory before being returned to the REPL and spoken
aloud (if a voice model is configured).

## Settings

`nexus.config` holds model name, Whisper size, listen duration, sample
rate, history length, TTS voice filename, and LLM timeout. Values can
be overridden by `data/settings.json` without changing code.

## Testing

Tests live in `tests/` and mock external processes (`ollama`, audio
devices) so the suite runs without a local model or hardware:

```
python -m unittest discover -s tests -v
```

## Roadmap alignment (Phase 1)

| Requirement                   | Status                                              |
|-------------------------------|-----------------------------------------------------|
| Voice input/output            | Whisper input + Piper output (wake word / VAD later)|
| Memory system                 | `session_memory` (in-memory + JSON persistence)     |
| Command-line interaction      | `nexus_loop()` REPL                                 |
| Config & settings manager     | `config.py` + optional `settings.json`              |
| Modular architecture          | `components/` package per concern                   |
| Logging & diagnostics         | TODO                                                |
| User identity/profile system  | TODO                                                |
