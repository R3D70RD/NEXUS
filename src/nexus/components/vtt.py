"""
Voice Input
Speech-to-text using Whisper. Returns None if the model or
audio backend cannot be initialized.
"""

import os

from nexus.config import get_settings

_model = None
_whisper_load_failed = False

# Size of each recording chunk, in seconds. Smaller = more responsive VAD.
_CHUNK_SECONDS = 0.25


def _load_whisper():
    global _model, _whisper_load_failed

    if _model is not None or _whisper_load_failed:
        return _model

    try:
        import whisper

        print("Loading Whisper model...")
        _model = whisper.load_model(get_settings().whisper_model)
        return _model
    except Exception as e:
        print(f"Failed to initialize Whisper dependencies: {e}")
        _whisper_load_failed = True
        return None


def wait_for_wake_word(wake_word: str):
    """Block until the wake word is heard, then return the transcription.

    Returns the transcribed text (which may still contain the wake word) or
    None if listening failed.
    """
    target = wake_word.lower().strip()
    if not target:
        return None

    while True:
        text = listen()
        if not text:
            return None
        if target in text.lower():
            return text


def _record_until_silence(sd, sample_rate: int, max_seconds: int,
                          silence_seconds: float, rms_threshold: float):
    """Record audio until the speaker pauses or `max_seconds` is reached.

    Uses a simple RMS-based voice activity detector: recording stops once
    speech has been detected and is followed by `silence_seconds` of quiet.
    Returns a list of float32 numpy chunks.
    """
    import numpy as np

    chunk_frames = int(_CHUNK_SECONDS * sample_rate)
    max_chunks = max(1, int(max_seconds / _CHUNK_SECONDS))
    silence_chunks_needed = max(1, int(silence_seconds / _CHUNK_SECONDS))

    chunks = []
    silent_run = 0
    has_speech = False

    for _ in range(max_chunks):
        chunk = sd.rec(
            chunk_frames,
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        chunks.append(chunk)

        rms = float(np.sqrt(np.mean(chunk ** 2)))
        if rms < rms_threshold:
            silent_run += 1
            if has_speech and silent_run >= silence_chunks_needed:
                break
        else:
            has_speech = True
            silent_run = 0

    return chunks


def listen():
    model = _load_whisper()
    if model is None:
        print("Whisper model is not loaded.")
        return None

    try:
        import numpy as np
        import sounddevice as sd
        from scipy.io.wavfile import write

        settings = get_settings()
        sample_rate = settings.sample_rate
        max_seconds = settings.listen_duration_seconds
        silence_seconds = settings.silence_duration_seconds
        rms_threshold = settings.silence_rms_threshold
        live_input_wav = str(settings.live_input_wav)

        print("\n NEXUS: Listening... ")
        chunks = _record_until_silence(
            sd, sample_rate, max_seconds, silence_seconds, rms_threshold
        )
        print("Recording finished. Transcribing...")

        if not chunks:
            return None

        audio_data = np.concatenate(chunks, axis=0)

        os.makedirs(os.path.dirname(live_input_wav), exist_ok=True)

        write(live_input_wav, sample_rate, audio_data)
        result = model.transcribe(live_input_wav, fp16=False)

        print("\n--- Transcription ---")
        return result["text"].strip()

    except Exception as e:
        print(f"Error while trying to listen: {e}")
        return None
