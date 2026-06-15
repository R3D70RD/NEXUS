"""Tests for the voice component, simulating absent audio hardware."""

import unittest
from unittest.mock import patch

from src.nexus.components import voice

class TestVoice(unittest.TestCase):

    def setUp(self):
        voice._voice = None
        voice._voice_load_failed = False

    def tearDown(self):
        voice._voice = None
        voice._voice_load_failed = False

    def test_speak_empty_text_is_noop(self):
        # Should not raise even with no model present
        voice.speak("")
        voice.speak(None)

    @patch("os.path.exists", return_value=False)
    def test_load_voice_missing_model_fails_gracefully(self, mock_exists):
        result = voice._load_voice()
        self.assertIsNone(result)
        self.assertTrue(voice._voice_load_failed)

    @patch("os.path.exists", return_value=False)
    def test_speak_without_model_does_not_raise(self, mock_exists):
        try:
            voice.speak("Voice system ready")
        except Exception as e:
            self.fail(f"speak() raised unexpectedly: {e}")

    @patch("os.path.exists", return_value=False)
    def test_is_available_false_without_model(self, mock_exists):
        self.assertFalse(voice.is_available())


if __name__ == "__main__":
    unittest.main()
