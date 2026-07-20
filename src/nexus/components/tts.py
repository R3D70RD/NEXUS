"""
Voice Output
Text-to-speech using Piper. Falls back to silent no-op if Piper
or the audio backend is unavailable, so NEXUS can still run
headless / text-only.
"""

import os
import re

VOICE_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "voices",
    "en_US-ljspeech-high.onnx"
)

_voice = None
_voice_load_failed = False


def _load_voice():
    global _voice, _voice_load_failed

    if _voice is not None or _voice_load_failed:
        return _voice

    try:
        from piper import PiperVoice

        if not os.path.exists(VOICE_MODEL_PATH):
            _voice_load_failed = True
            return None

        _voice = PiperVoice.load(VOICE_MODEL_PATH)
        return _voice
    except Exception:
        _voice_load_failed = True
        return None


import re

def clean_for_tts(text: str) -> str:
    """Strip ANSI escape sequences, markdown, and special formatting for smooth TTS playback."""
    if not text:
        return ""

    # 1. Remove ANSI escape codes (e.g., \u001b[10D, \u001b[K, \033[2J)
    # This targets CSI sequences (Control Sequence Introducer) common in terminal outputs
    ansi_escape = re.compile(r'(?:\x1b|\u001b)\[[0-9?]*[a-zA-Z]')
    text = ansi_escape.sub('', text)

    # 2. Remove specific terminal clearing/erase artifacts that might leave behind raw character fragments
    text = re.sub(r'(?:\x1b|\u001b)[K]', '', text)

    # 3. Handle specific text-based UI separators and structural symbols
    text = re.sub(r'-{2,}', ' ', text)                  # Remove horizontal rules like "---"
    text = re.sub(r'[\u2192\u25b6\u279c➔➔→]', ' to ', text) # Convert arrows (→) to the spoken word "to"
    text = re.sub(r'[\u2014\u2013—–]', ', ', text)       # Convert em/en dashes to commas for a natural speaking pause

    # 4. Remove code blocks entirely
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # 5. Bold / italics (** ** , * *, __ __ , _ _)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)

    # 6. Inline code
    text = re.sub(r'`(.*?)`', r'\1', text)

    # 7. Markdown headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # 8. Bullets and List Numbers (e.g., "1. **Cognitive**" -> "1. Cognitive")
    # Clean bullet characters
    text = re.sub(r'^\s*[-•*]\s*', '', text, flags=re.MULTILINE)
    # Ensure numbered lists have a clean space after the digit so TTS handles it as a sentence pause
    text = re.sub(r'^\s*(\d+)\.\s*', r'\1. ', text, flags=re.MULTILINE)

    # 9. Links: [label](url) -> label
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # 10. Strikethrough ~~text~~ -> text
    text = re.sub(r'~~(.*?)~~', r'\1', text)

    # 11. Leftover stray markdown/formatting characters
    text = re.sub(r'[*_~`#>]', '', text)

    # 12. Collapse extra whitespace/newlines into natural sentence pauses
    text = re.sub(r'\n{2,}', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Fix potential double periods caused by combining newlines and existing punctuation
    text = re.sub(r'\.{2,}', '.', text)

    return text.strip()


def speak(text: str):
    """Synthesize and play `text`. Silently no-ops if TTS is unavailable."""
    if not text:
        return

    text = clean_for_tts(text)

    if not text:
        return

    voice = _load_voice()
    if voice is None:
        return

    try:
        import numpy as np
        import sounddevice as sd

        audio_chunks = []

        for chunk in voice.synthesize(text):
            audio_chunks.append(chunk.audio_int16_array)

        if not audio_chunks:
            return

        audio = np.concatenate(audio_chunks)

        sd.play(audio, samplerate=22050)
        sd.wait()
    except Exception:
        # Audio output failed (e.g. no audio device); fail silently.
        pass


def is_available() -> bool:
    """Return True if the voice backend loaded successfully."""
    return _load_voice() is not None