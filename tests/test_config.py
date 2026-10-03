"""Tests for runtime settings."""

import json
import os
import tempfile
import unittest

import pathsetup  # noqa: F401

from nexus import config


class TestConfig(unittest.TestCase):

    def tearDown(self):
        config.load_settings()

    def test_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = config.load_settings(data_dir=tmpdir)
            self.assertEqual(settings.model, "ministral-3")
            self.assertEqual(settings.max_history, 10)
            self.assertTrue(str(settings.history_file).endswith("session_history.json"))
            self.assertTrue(str(settings.voice_model_path).endswith("en_US-ljspeech-high.onnx"))

    def test_load_overrides_from_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"model": "llama3", "max_history": 4}, handle)

            settings = config.load_settings(path, data_dir=tmpdir)
            self.assertEqual(settings.model, "llama3")
            self.assertEqual(settings.max_history, 4)

    def test_load_ignores_unknown_and_bad_types(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"model": "ok", "max_history": "nope", "extra": 1}, handle)

            settings = config.load_settings(path, data_dir=tmpdir)
            self.assertEqual(settings.model, "ok")
            self.assertEqual(settings.max_history, 10)

    def test_corrupted_file_uses_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("{not json")

            settings = config.load_settings(path, data_dir=tmpdir)
            self.assertEqual(settings.model, "ministral-3")

    def test_save_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = config.load_settings(data_dir=tmpdir)
            settings.model = "custom-model"
            dest = os.path.join(tmpdir, "settings.json")
            config.save_settings(dest)

            config.load_settings()
            reloaded = config.load_settings(dest, data_dir=tmpdir)
            self.assertEqual(reloaded.model, "custom-model")
            with open(dest, encoding="utf-8") as handle:
                saved = json.load(handle)
            self.assertNotIn("data_dir", saved)


if __name__ == "__main__":
    unittest.main()
