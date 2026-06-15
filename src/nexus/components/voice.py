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


def clean_for_tts(text: str) -> str:
    """Strip markdown/code formatting so TTS doesn't read out symbols."""
    if not text:
        return ""

    # Remove code blocks entirely
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Bold / italics (** ** , * *, __ __ , _ _)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)

    # Inline code
    text = re.sub(r'`(.*?)`', r'\1', text)

    # Markdown headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Bullets
    text = re.sub(r'^\s*[-•*]\s*', '', text, flags=re.MULTILINE)

    # Links: [label](url) -> label
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # Strikethrough ~~text~~ -> text
    text = re.sub(r'~~(.*?)~~', r'\1', text)

    # Leftover stray markdown/formatting characters
    text = re.sub(r'[*_~`#>]', '', text)

    # Collapse extra whitespace/newlines
    text = re.sub(r'\n{2,}', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)

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