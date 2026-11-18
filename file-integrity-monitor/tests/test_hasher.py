"""
test_hasher.py — Unit Tests for hasher.py
==========================================
Tests the SHA-256 hashing engine in isolation.

Run from the project root:
    python -m unittest tests/test_hasher.py -v
"""

import os
import sys
import tempfile
import unittest

# Allow imports from the project root (one level up from tests/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hasher import hash_file, hash_folder


class TestHashFile(unittest.TestCase):
    """Tests for hash_file() — single file hashing."""

    def setUp(self):
        """Create a temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove all temporary test files after each test."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _make_file(self, name, content="Hello, FIM!"):
        """Helper: create a named file with given text content."""
        path = os.path.join(self.test_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    # ── Test 1: hash_file returns a 64-character hex string ──────────────────
    def test_hash_returns_64_char_hex(self):
        """SHA-256 digest must be exactly 64 hexadecimal characters."""
        path = self._make_file("sample.txt", "Cybersecurity with Python")
        result = hash_file(path)

        self.assertIsNotNone(result, "hash_file() returned None for a readable file")
        self.assertEqual(len(result), 64, "SHA-256 hex digest must be 64 characters")
        self.assertTrue(
            all(c in "0123456789abcdef" for c in result),
            "Hash must contain only hex characters (0-9, a-f)"
        )

    # ── Test 2: SHA-256 is deterministic — same content = same hash ───────────
    def test_same_content_produces_same_hash(self):
        """Two files with identical content must produce the same hash."""
        path1 = self._make_file("file1.txt", "Identical content")
        path2 = self._make_file("file2.txt", "Identical content")

        self.assertEqual(
            hash_file(path1), hash_file(path2),
            "Same content must always produce the same SHA-256 hash"
        )

    # ── Test 3: Different content produces a different hash (avalanche) ───────
    def test_different_content_produces_different_hash(self):
        """Even a one-character difference must produce a completely different hash."""
        path1 = self._make_file("original.txt", "Hello, World!")
        path2 = self._make_file("modified.txt", "Hello, World?")  # ! -> ?

        self.assertNotEqual(
            hash_file(path1), hash_file(path2),
            "Different content must produce different hashes (avalanche effect)"
        )

    # ── Test 4: Missing file returns None gracefully ──────────────────────────
    def test_missing_file_returns_none(self):
        """hash_file() on a non-existent path must return None, not raise."""
        result = hash_file(os.path.join(self.test_dir, "ghost_file.txt"))
        self.assertIsNone(result, "Missing file must return None, not raise an exception")

    # ── Test 5: Empty file is hashed successfully ─────────────────────────────
    def test_empty_file_returns_hash(self):
        """An empty file is valid — SHA-256 of empty content is well-defined."""
        path = self._make_file("empty.txt", "")
        result = hash_file(path)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 64)
        # SHA-256 of empty bytes is the well-known constant below
        self.assertEqual(
            result,
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )


class TestHashFolder(unittest.TestCase):
    """Tests for hash_folder() — recursive directory scanning."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _make_file(self, rel_path, content="data"):
        """Create a file (and any needed subdirs) relative to test_dir."""
        full_path = os.path.join(self.test_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return full_path

    # ── Test 6: hash_folder scans multiple files ──────────────────────────────
    def test_scans_multiple_files(self):
        """hash_folder() must return an entry for every file in the directory."""
        self._make_file("employee.txt",    "John Doe")
        self._make_file("confidential.txt","TOP SECRET")
        self._make_file("report.txt",      "Monthly report")

        result = hash_folder(self.test_dir)

        self.assertEqual(len(result), 3, "Should hash all 3 files")
        self.assertIn("employee.txt",     result)
        self.assertIn("confidential.txt", result)
        self.assertIn("report.txt",       result)

    # ── Test 7: Keys are relative paths, not absolute ─────────────────────────
    def test_keys_are_relative_paths(self):
        """Keys in the returned dict must be paths relative to the scanned folder."""
        self._make_file("notes.txt", "some content")
        result = hash_folder(self.test_dir)

        for key in result:
            self.assertFalse(
                os.path.isabs(key),
                f"Key '{key}' must be relative, not absolute"
            )

    # ── Test 8: Recursive scan finds files in subdirectories ─────────────────
    def test_recursive_scan_finds_nested_files(self):
        """hash_folder() must descend into subdirectories."""
        self._make_file("root.txt",              "root level")
        self._make_file(os.path.join("sub", "nested.txt"), "nested level")

        result = hash_folder(self.test_dir)

        self.assertIn("root.txt",                      result)
        self.assertIn(os.path.join("sub", "nested.txt"), result)
        self.assertEqual(len(result), 2)

    # ── Test 9: Empty folder returns empty dict ───────────────────────────────
    def test_empty_folder_returns_empty_dict(self):
        """Scanning an empty folder must return {}, not raise."""
        result = hash_folder(self.test_dir)
        self.assertEqual(result, {})

    # ── Test 10: Non-existent folder returns empty dict ───────────────────────
    def test_invalid_folder_returns_empty_dict(self):
        """Scanning a path that does not exist must return {}, not raise."""
        result = hash_folder(os.path.join(self.test_dir, "does_not_exist"))
        self.assertEqual(result, {})

    # ── Test 11: exclude_paths prevents those dirs from being scanned ─────────
    def test_exclude_paths_are_skipped(self):
        """Files inside an excluded directory must not appear in the result."""
        self._make_file("keep.txt",                    "include me")
        excluded_dir = os.path.join(self.test_dir, "skip_this")
        self._make_file(os.path.join("skip_this", "secret.txt"), "exclude me")

        result = hash_folder(
            self.test_dir,
            exclude_paths={os.path.abspath(excluded_dir)}
        )

        self.assertIn("keep.txt", result)
        self.assertNotIn(os.path.join("skip_this", "secret.txt"), result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
