"""
test_baseline.py — Unit Tests for baseline.py
==============================================
Tests saving and loading of baseline JSON and alerts JSON.

Run from the project root:
    python -m unittest tests/test_baseline.py -v
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from baseline import save_baseline, load_baseline, save_alerts, load_alerts


class TestSaveAndLoadBaseline(unittest.TestCase):
    """Tests for save_baseline() and load_baseline()."""

    def setUp(self):
        """Point all file operations to a fresh temporary directory."""
        self.tmp_dir  = tempfile.mkdtemp()
        self.bl_path  = os.path.join(self.tmp_dir, "baseline.json")
        self.sample   = {
            "employee.txt":    "aabbcc112233",
            "confidential.txt":"ddeeff445566",
            "report.txt":      "aabbcc778899",
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # ── Test 1: save_baseline creates a JSON file ─────────────────────────────
    def test_save_baseline_creates_file(self):
        """save_baseline() must create the JSON file on disk."""
        result = save_baseline(self.sample, baseline_path=self.bl_path)
        self.assertTrue(result,                       "save_baseline() must return True on success")
        self.assertTrue(os.path.isfile(self.bl_path), "baseline.json must exist after saving")

    # ── Test 2: saved file is valid JSON with correct structure ───────────────
    def test_saved_file_has_correct_json_structure(self):
        """The saved JSON must include 'files', 'created_at', and 'file_count'."""
        save_baseline(self.sample, monitored_directory="C:\\TestFolder",
                      baseline_path=self.bl_path)
        with open(self.bl_path, "r") as f:
            data = json.load(f)

        self.assertIn("files",               data)
        self.assertIn("created_at",          data)
        self.assertIn("monitored_directory", data)
        self.assertIn("file_count",          data)
        self.assertEqual(data["file_count"],       3)
        self.assertEqual(data["monitored_directory"], "C:\\TestFolder")

    # ── Test 3: load_baseline returns the original hash dict ─────────────────
    def test_load_baseline_returns_correct_hash_dict(self):
        """load_baseline() must return exactly the same dict that was saved."""
        save_baseline(self.sample, baseline_path=self.bl_path)
        hash_dict, metadata = load_baseline(baseline_path=self.bl_path)

        self.assertIsNotNone(hash_dict)
        self.assertEqual(hash_dict, self.sample,
                         "Loaded hash dict must match the original saved dict")

    # ── Test 4: load_baseline returns metadata ────────────────────────────────
    def test_load_baseline_returns_metadata(self):
        """load_baseline() must return a non-None metadata dict."""
        save_baseline(self.sample, monitored_directory="D:\\Docs",
                      baseline_path=self.bl_path)
        _, metadata = load_baseline(baseline_path=self.bl_path)

        self.assertIsNotNone(metadata)
        self.assertIn("created_at",          metadata)
        self.assertIn("monitored_directory", metadata)
        self.assertEqual(metadata["monitored_directory"], "D:\\Docs")

    # ── Test 5: load_baseline returns (None, None) when file missing ──────────
    def test_load_baseline_missing_file(self):
        """load_baseline() must return (None, None) if no baseline exists."""
        hash_dict, metadata = load_baseline(
            baseline_path=os.path.join(self.tmp_dir, "no_such_file.json")
        )
        self.assertIsNone(hash_dict)
        self.assertIsNone(metadata)

    # ── Test 6: load_baseline handles corrupted JSON gracefully ───────────────
    def test_load_baseline_corrupted_json(self):
        """load_baseline() must return (None, None) on a corrupt JSON file."""
        with open(self.bl_path, "w") as f:
            f.write("{ this is not valid JSON !!!}")

        hash_dict, metadata = load_baseline(baseline_path=self.bl_path)
        self.assertIsNone(hash_dict,  "Corrupted baseline must return None for hash_dict")
        self.assertIsNone(metadata,   "Corrupted baseline must return None for metadata")

    # ── Test 7: load_baseline handles legacy flat format ─────────────────────
    def test_load_baseline_legacy_flat_format(self):
        """load_baseline() must also handle old flat-format baselines (no 'files' key)."""
        # Write an old-style flat baseline (direct path -> hash mapping)
        with open(self.bl_path, "w") as f:
            json.dump({"old_file.txt": "oldhash123"}, f)

        hash_dict, metadata = load_baseline(baseline_path=self.bl_path)
        self.assertIsNotNone(hash_dict)
        self.assertIn("old_file.txt", hash_dict)


class TestSaveAndLoadAlerts(unittest.TestCase):
    """Tests for save_alerts() and load_alerts()."""

    def setUp(self):
        self.tmp_dir    = tempfile.mkdtemp()
        self.alert_path = os.path.join(self.tmp_dir, "last_alerts.json")
        self.changes = {
            "modified": ["employee.txt"],
            "deleted":  ["confidential.txt"],
            "new":      ["unknown.txt"],
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # ── Test 8: save_alerts creates a JSON file ───────────────────────────────
    def test_save_alerts_creates_file(self):
        """save_alerts() must create the alerts JSON file."""
        save_alerts(self.changes, alerts_path=self.alert_path)
        self.assertTrue(os.path.isfile(self.alert_path))

    # ── Test 9: load_alerts returns the saved changes dict ────────────────────
    def test_load_alerts_returns_correct_changes(self):
        """load_alerts() must return the same changes that were saved."""
        save_alerts(self.changes, monitored_directory="C:\\TestFolder",
                    alerts_path=self.alert_path)
        loaded_changes, metadata = load_alerts(alerts_path=self.alert_path)

        self.assertIsNotNone(loaded_changes)
        self.assertEqual(loaded_changes["modified"], ["employee.txt"])
        self.assertEqual(loaded_changes["deleted"],  ["confidential.txt"])
        self.assertEqual(loaded_changes["new"],      ["unknown.txt"])

    # ── Test 10: load_alerts returns (None, None) when file missing ───────────
    def test_load_alerts_missing_file(self):
        """load_alerts() must return (None, None) when no alerts file exists."""
        changes, metadata = load_alerts(
            alerts_path=os.path.join(self.tmp_dir, "missing.json")
        )
        self.assertIsNone(changes)
        self.assertIsNone(metadata)


if __name__ == "__main__":
    unittest.main(verbosity=2)
