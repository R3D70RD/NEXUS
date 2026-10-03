"""Tests for the session memory component."""

import os
import tempfile
import unittest
import json

import pathsetup  # noqa: F401

from nexus.components import session_memory
from nexus.config import load_settings


class TestSessionMemory(unittest.TestCase):

    def setUp(self):
        session_memory.clear()
        self._tmpdir = tempfile.TemporaryDirectory()
        load_settings(data_dir=self._tmpdir.name)

    def tearDown(self):
        session_memory.clear()
        load_settings()
        self._tmpdir.cleanup()

    def test_add_message_and_context(self):
        session_memory.add_message("user", "hello")
        session_memory.add_message("NEXUS", "hi there")

        context = session_memory.get_context()
        self.assertIn("User: hello", context)
        self.assertIn("Nexus: hi there", context)

    def test_history_trimmed_to_max(self):
        from nexus.config import get_settings

        limit = get_settings().max_history
        for i in range(limit + 5):
            session_memory.add_message("user", f"msg{i}")

        history = session_memory.get_history()
        self.assertEqual(len(history), limit)
        self.assertEqual(history[0]["content"], f"msg{5}")

    def test_clear(self):
        session_memory.add_message("user", "hello")
        session_memory.clear()
        self.assertEqual(session_memory.get_history(), [])

    def test_save_and_load(self):
        history_file = os.path.join(self._tmpdir.name, "session_history.json")

        session_memory.add_message("user", "persisted message")
        session_memory.save(history_file)

        session_memory.clear()
        self.assertEqual(session_memory.get_history(), [])

        session_memory.load(history_file)
        history = session_memory.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["content"], "persisted message")

        with open(history_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)

    def test_load_missing_file_is_noop(self):
        history_file = os.path.join(self._tmpdir.name, "does_not_exist.json")
        session_memory.clear()
        session_memory.load(history_file)
        self.assertEqual(session_memory.get_history(), [])


if __name__ == "__main__":
    unittest.main()
