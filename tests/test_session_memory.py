"""Tests for the session memory component."""

import os
import tempfile
import unittest
import json

from src.nexus.components import session_memory

class TestSessionMemory(unittest.TestCase):

    def setUp(self):
        session_memory.clear()

    def tearDown(self):
        session_memory.clear()

    def test_add_message_and_context(self):
        session_memory.add_message("user", "hello")
        session_memory.add_message("NEXUS", "hi there")

        context = session_memory.get_context()
        self.assertIn("User: hello", context)
        self.assertIn("Nexus: hi there", context)

    def test_history_trimmed_to_max(self):
        for i in range(session_memory.MAX_HISTORY + 5):
            session_memory.add_message("user", f"msg{i}")

        history = session_memory.get_history()
        self.assertEqual(len(history), session_memory.MAX_HISTORY)
        # Oldest messages should have been dropped
        self.assertEqual(history[0]["content"], "msg5")

    def test_clear(self):
        session_memory.add_message("user", "hello")
        session_memory.clear()
        self.assertEqual(session_memory.get_history(), [])

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = os.path.join(tmpdir, "session_history.json")

            original_path = session_memory.HISTORY_FILE
            session_memory.HISTORY_FILE = history_file
            try:
                session_memory.add_message("user", "persisted message")
                session_memory.save()

                session_memory.clear()
                self.assertEqual(session_memory.get_history(), [])

                session_memory.load()
                history = session_memory.get_history()
                self.assertEqual(len(history), 1)
                self.assertEqual(history[0]["content"], "persisted message")

                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.assertEqual(len(data), 1)
            finally:
                session_memory.HISTORY_FILE = original_path

    def test_load_missing_file_is_noop(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = os.path.join(tmpdir, "does_not_exist.json")

            original_path = session_memory.HISTORY_FILE
            session_memory.HISTORY_FILE = history_file
            try:
                session_memory.clear()
                session_memory.load()
                self.assertEqual(session_memory.get_history(), [])
            finally:
                session_memory.HISTORY_FILE = original_path


if __name__ == "__main__":
    unittest.main()
