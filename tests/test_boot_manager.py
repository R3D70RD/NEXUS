"""Tests for the boot manager component."""

import os
import tempfile
import unittest

from src.nexus.components import boot_manager

class TestBootTracker(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmpdir.name, "boot_state.json")

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_first_boot_returns_one(self):
        tracker = BootTracker(self.path)
        self.assertEqual(tracker.boot(), 1)

    def test_boot_increments_persisted_counter(self):
        tracker = BootTracker(self.path)
        self.assertEqual(tracker.boot(), 1)
        self.assertEqual(tracker.boot(), 2)
        self.assertEqual(tracker.boot(), 3)

    def test_get_count_without_incrementing(self):
        tracker = BootTracker(self.path)
        tracker.boot()
        tracker.boot()
        self.assertEqual(tracker.get_count(), 2)
        self.assertEqual(tracker.get_count(), 2)

    def test_reset(self):
        tracker = BootTracker(self.path)
        tracker.boot()
        tracker.boot()
        tracker.reset()
        self.assertEqual(tracker.get_count(), 0)

    def test_corrupted_file_recovers(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{not valid json")

        tracker = BootTracker(self.path)
        self.assertEqual(tracker.boot(), 1)

    def test_persistence_across_instances(self):
        tracker1 = BootTracker(self.path)
        tracker1.boot()
        tracker1.boot()

        tracker2 = BootTracker(self.path)
        self.assertEqual(tracker2.get_count(), 2)
        self.assertEqual(tracker2.boot(), 3)


if __name__ == "__main__":
    unittest.main()
