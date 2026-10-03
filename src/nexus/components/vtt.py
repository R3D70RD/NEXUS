"""
Voice Input
Speech-to-text using Whisper. Returns None if the model or
audio backend cannot be initialized.
"""

import os

from nexus.config import get_settings

_model = None
_whisper_load_failed = False


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


def listen():
    model = _load_whisper()
    if model is None:
        print("Whisper model is not loaded.")
        return None

    try:
        import sounddevice as sd
        from scipy.io.wavfile import write

        settings = get_settings()
        sample_rate = settings.sample_rate
        duration = settings.listen_duration_seconds
        live_input_wav = str(settings.live_input_wav)

        print("\n NEXUS: Listening... ")
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32"
        )
        sd.wait()
        print("Recording finished. Transcribing...")

        os.makedirs(os.path.dirname(live_input_wav), exist_ok=True)

        write(live_input_wav, sample_rate, audio_data)
        result = model.transcribe(live_input_wav, fp16=False)

        print("\n--- Transcription ---")
        return result["text"].strip()

    except Exception as e:
        print(f"Error while trying to listen: {e}")
        return None
