import os

# Initialize global state tracking variables
_model = None
_whisper_load_failed = False

SAMPLE_RATE = 16000
DURATION = 5

# Fixed missing comma
WHISPER_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "input",               # Added comma here
    "live_input.wav"
)

def _load_whisper():
    global _model, _whisper_load_failed

    if _model is not None or _whisper_load_failed:
        return _model

    try:
        # We import these globally here so they are accessible in listen()
        global np, sd, whisper, write
        import numpy as np
        import sounddevice as sd 
        import whisper
        from scipy.io.wavfile import write 

        print("🤖 Loading Whisper 'small' model...")
        _model = whisper.load_model("small")
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
        print("\n NEXUS: Listening... ")
        # Record audio as float32, mono channel
        audio_data = sd.rec(
            int(DURATION * SAMPLE_RATE), 
            samplerate=SAMPLE_RATE, 
            channels=1, 
            dtype="float32"
        )
        sd.wait()  # Wait until the recording is finished
        print("Recording finished. Transcribing...") # how to make the system wait only when user stopped talking for a few seconds?

        # Ensure the target directory exists before saving
        os.makedirs(os.path.dirname(WHISPER_MODEL_PATH), exist_ok=True)

        # Used WHISPER_MODEL_PATH instead of undefined FILENAME
        write(WHISPER_MODEL_PATH, SAMPLE_RATE, audio_data)
        result = model.transcribe(WHISPER_MODEL_PATH, fp16=False)

        print("\n--- Transcription ---")
        return result["text"].strip()
        
    except Exception as e:
        print(f"Error while trying to listen: {e}")
        return None