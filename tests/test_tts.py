"""Tests for the TTS component, simulating absent audio hardware."""

import unittest
from unittest.mock import patch

import pathsetup  # noqa: F401

from nexus.components import tts


class TestTTS(unittest.TestCase):

    def setUp(self):
        tts._voice = None
        tts._voice_load_failed = False

    def tearDown(self):
        tts._voice = None
        tts._voice_load_failed = False

    def test_speak_empty_text_is_noop(self):
        tts.speak("")
        tts.speak(None)

    @patch("os.path.exists", return_value=False)
    def test_load_voice_missing_model_fails_gracefully(self, mock_exists):
        result = tts._load_voice()
        self.assertIsNone(result)
        self.assertTrue(tts._voice_load_failed)

    @patch("os.path.exists", return_value=False)
    def test_speak_without_model_does_not_raise(self, mock_exists):
        try:
            tts.speak("Voice system ready")
        except Exception as e:
            self.fail(f"speak() raised unexpectedly: {e}")

    @patch("os.path.exists", return_value=False)
    def test_is_available_false_without_model(self, mock_exists):
        self.assertFalse(tts.is_available())


if __name__ == "__main__":
    unittest.main()
