# NEXUS - Architecture

## Overview

NEXUS Core is the orchestrator and entry point for the system described
in the Phase 1 roadmap: a local-first, modular AI assistant running on
top of Ollama, with session memory, voice I/O, and a structured boot
sequence.

## Module Map

```
src/ai_infrastructure/
├── main.py                     # Boot sequence, logic gate, agentic loop
├── components/
│   ├── boot_manager.py         # First-run detection, persistent boot counter
│   ├── session_memory.py       # Short-term conversation history (in-memory + disk)
│   ├── llm_provider.py         # Ollama wrapper (ask, list_models, pull_model)
│   └── voice.py                # Piper TTS output with silent fallback
└── data/
    ├── boot_state.json         # Persisted boot counter (not included)
    ├── session_history.json    # Persisted conversation history (created at runtime)
    └── voices/                 # Piper voice models (not included)
```

## Boot Sequence

1. `BootTracker.boot()` increments the persisted boot counter.
2. If this is boot #1, `setup()` runs (checks Ollama is installed).
3. `pre_warm()` verifies Ollama is installed and the target model
   (`ministral-3` by default) is available, offering to pull it if not.
4. `nexus_loop()` starts the terminal REPL, loading any saved session
   history from disk.

## Logic Gate

`nexus_run()` is the core gate: every user turn is appended to session
memory, the full conversation context is assembled with `BASE_PROMPT`,
sent to the local LLM via `llm_provider.ask()`, and the response is
stored back into memory before being returned to the REPL and spoken
aloud (if a voice model is configured).

## Testing

Tests live in `tests/` and mock all external processes (`ollama`,
audio devices) so the suite runs without any local model or hardware
installed:

```
python -m unittest discover -s tests -v
```

## Roadmap alignment (Phase 1)

| Requirement                  | Status                                      |
|-------------------------------|----------------------------------------------|
| Voice input/output            | Voice output via Piper (input not yet wired) |
| Memory system                  | `session_memory` (in-memory + JSON persistence) |
| Command-line interaction       | `nexus_loop()` REPL                          |
| Local file access               | `data/` directory, JSON state                |
| Config & settings manager       | `MODEL` constant; extend with config.py later |
| Modular architecture            | `components/` package per concern            |
| Logging & diagnostics            | TODO - not yet implemented                   |
| User identity/profile system     | TODO - not yet implemented                   |
