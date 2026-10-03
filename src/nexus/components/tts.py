"""
Voice Output
Text-to-speech using Piper. Falls back to silent no-op if Piper
or the audio backend is unavailable, so NEXUS can still run
headless / text-only.
"""

import os
import re

from nexus.config import get_settings

_voice = None
_voice_load_failed = False


def _voice_model_path() -> str:
    return str(get_settings().voice_model_path)


def _load_voice():
    global _voice, _voice_load_failed

    if _voice is not None or _voice_load_failed:
        return _voice

    try:
        from piper import PiperVoice

        path = _voice_model_path()
        if not os.path.exists(path):
            _voice_load_failed = True
            return None

        _voice = PiperVoice.load(path)
        return _voice
    except Exception:
        _voice_load_failed = True
        return None


def clean_for_tts(text: str) -> str:
    """Strip ANSI escape sequences, markdown, and special formatting for smooth TTS playback."""
    if not text:
        return ""

    ansi_escape = re.compile(r'(?:\x1b|\u001b)\[[0-9?]*[a-zA-Z]')
    text = ansi_escape.sub('', text)

    text = re.sub(r'(?:\x1b|\u001b)[K]', '', text)

    text = re.sub(r'-{2,}', ' ', text)
    text = re.sub(r'[\u2192\u25b6\u279c➔➔→]', ' to ', text)
    text = re.sub(r'[\u2014\u2013—–]', ', ', text)

    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)

    text = re.sub(r'`(.*?)`', r'\1', text)

    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    text = re.sub(r'^\s*[-•*]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*(\d+)\.\s*', r'\1. ', text, flags=re.MULTILINE)

    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    text = re.sub(r'~~(.*?)~~', r'\1', text)

    text = re.sub(r'[*_~`#>]', '', text)

    text = re.sub(r'\n{2,}', '. ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)

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
        pass


def is_available() -> bool:
    """Return True if the voice backend loaded successfully."""
    return _load_voice() is not None
