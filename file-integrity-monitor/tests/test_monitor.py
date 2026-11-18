"""
test_monitor.py — Unit Tests for monitor.py
============================================
Tests the core change-detection logic in complete isolation.
No files are read or written — only pure dictionary comparisons.

Run from the project root:
    python -m unittest tests/test_monitor.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor import detect_changes, has_any_changes, count_changes


class TestDetectChanges(unittest.TestCase):
    """Tests for detect_changes() — the core FIM logic."""

    # ── Test 1: Detect a modified file ───────────────────────────────────────
    def test_detects_modified_file(self):
        """A file whose hash changed between baseline and current must be MODIFIED."""
        baseline = {"employee.txt": "hash_original"}
        current  = {"employee.txt": "hash_different"}   # hash changed

        changes = detect_changes(baseline, current)

        self.assertIn("employee.txt", changes["modified"],
                      "File with changed hash must appear in 'modified'")
        self.assertEqual(len(changes["deleted"]), 0)
        self.assertEqual(len(changes["new"]),     0)

    # ── Test 2: Detect a deleted file ────────────────────────────────────────
    def test_detects_deleted_file(self):
        """A file in the baseline that is absent in the current scan must be DELETED."""
        baseline = {"confidential.txt": "hash_abc"}
        current  = {}   # file is gone

        changes = detect_changes(baseline, current)

        self.assertIn("confidential.txt", changes["deleted"],
                      "File missing from current scan must appear in 'deleted'")
        self.assertEqual(len(changes["modified"]), 0)
        self.assertEqual(len(changes["new"]),      0)

    # ── Test 3: Detect a new file ─────────────────────────────────────────────
    def test_detects_new_file(self):
        """A file in the current scan that was absent in the baseline must be NEW."""
        baseline = {}
        current  = {"unknown.txt": "hash_xyz"}   # file appeared after baseline

        changes = detect_changes(baseline, current)

        self.assertIn("unknown.txt", changes["new"],
                      "File absent from baseline must appear in 'new'")
        self.assertEqual(len(changes["modified"]), 0)
        self.assertEqual(len(changes["deleted"]),  0)

    # ── Test 4: Identify unchanged files ─────────────────────────────────────
    def test_unchanged_files_not_flagged(self):
        """Files with matching hashes must NOT appear in any change category."""
        same_hash = "aabbcc112233445566"
        baseline  = {"report.txt": same_hash}
        current   = {"report.txt": same_hash}   # identical hash

        changes = detect_changes(baseline, current)

        self.assertEqual(len(changes["modified"]), 0,
                         "Unchanged file must not appear in 'modified'")
        self.assertEqual(len(changes["deleted"]),  0,
                         "Unchanged file must not appear in 'deleted'")
        self.assertEqual(len(changes["new"]),      0,
                         "Unchanged file must not appear in 'new'")

    # ── Test 5: Detect all three change types simultaneously ─────────────────
    def test_detects_all_three_change_types_at_once(self):
        """The full real-world demo scenario — all three change types in one scan."""
        baseline = {
            "employee.txt":    "original_hash",
            "confidential.txt":"secret_hash",
            "report.txt":      "report_hash",   # unchanged
        }
        current = {
            "employee.txt": "modified_hash",    # content changed
            # confidential.txt missing           # deleted
            "report.txt":   "report_hash",      # unchanged
            "unknown.txt":  "new_hash",         # new file appeared
        }

        changes = detect_changes(baseline, current)

        self.assertIn("employee.txt",     changes["modified"])
        self.assertIn("confidential.txt", changes["deleted"])
        self.assertIn("unknown.txt",      changes["new"])
        self.assertNotIn("report.txt",    changes["modified"])
        self.assertNotIn("report.txt",    changes["deleted"])
        self.assertNotIn("report.txt",    changes["new"])

    # ── Test 6: Both dicts empty — no changes ─────────────────────────────────
    def test_empty_baseline_and_current_no_changes(self):
        """Two empty dicts must produce zero changes."""
        changes = detect_changes({}, {})
        self.assertEqual(len(changes["modified"]), 0)
        self.assertEqual(len(changes["deleted"]),  0)
        self.assertEqual(len(changes["new"]),      0)

    # ── Test 7: Empty baseline — all files are new ────────────────────────────
    def test_empty_baseline_all_files_new(self):
        """When baseline is empty, every current file must be classified as NEW."""
        current = {"a.txt": "h1", "b.txt": "h2", "c.txt": "h3"}
        changes = detect_changes({}, current)

        self.assertEqual(set(changes["new"]), {"a.txt", "b.txt", "c.txt"})
        self.assertEqual(len(changes["modified"]), 0)
        self.assertEqual(len(changes["deleted"]),  0)

    # ── Test 8: Empty current scan — all files deleted ────────────────────────
    def test_empty_current_all_files_deleted(self):
        """When nothing is found in current scan, all baseline files must be DELETED."""
        baseline = {"a.txt": "h1", "b.txt": "h2"}
        changes  = detect_changes(baseline, {})

        self.assertEqual(set(changes["deleted"]), {"a.txt", "b.txt"})
        self.assertEqual(len(changes["modified"]), 0)
        self.assertEqual(len(changes["new"]),      0)

    # ── Test 9: Results are sorted ────────────────────────────────────────────
    def test_results_are_sorted_alphabetically(self):
        """Each change list must be sorted so reports are consistent and readable."""
        baseline = {"c.txt": "h1", "a.txt": "h2", "b.txt": "h3"}
        current  = {}   # all deleted

        changes = detect_changes(baseline, current)

        self.assertEqual(changes["deleted"], ["a.txt", "b.txt", "c.txt"],
                         "Deleted list must be sorted alphabetically")


class TestHasAnyChanges(unittest.TestCase):
    """Tests for has_any_changes()."""

    # ── Test 10: Returns False when nothing changed ───────────────────────────
    def test_returns_false_when_no_changes(self):
        no_changes = {"modified": [], "deleted": [], "new": []}
        self.assertFalse(has_any_changes(no_changes))

    # ── Test 11: Returns True when at least one change exists ─────────────────
    def test_returns_true_when_changes_exist(self):
        with_changes = {"modified": ["file.txt"], "deleted": [], "new": []}
        self.assertTrue(has_any_changes(with_changes))


class TestCountChanges(unittest.TestCase):
    """Tests for count_changes()."""

    # ── Test 12: Returns correct counts and total ─────────────────────────────
    def test_correct_counts_and_total(self):
        changes = {
            "modified": ["a.txt", "b.txt"],
            "deleted":  ["c.txt"],
            "new":      ["d.txt", "e.txt", "f.txt"],
        }
        result = count_changes(changes)

        self.assertEqual(result["modified"], 2)
        self.assertEqual(result["deleted"],  1)
        self.assertEqual(result["new"],      3)
        self.assertEqual(result["total"],    6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
