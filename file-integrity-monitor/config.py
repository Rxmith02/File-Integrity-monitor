"""
config.py — Central Application Configuration
===============================================
All tuneable settings live here so you never need to hunt through
multiple files to change a value.

Rule: Import from this module, never hard-code values in other modules.

Usage:
    from config import CHUNK_SIZE, BASELINE_PATH, ...
"""

import os

# ── Application metadata ───────────────────────────────────────────────────────

APP_NAME    = "File Integrity Monitoring System"
APP_VERSION = "1.0.0"
APP_AUTHOR  = "FIM Project"

# ── Hashing settings ───────────────────────────────────────────────────────────

# Which hash algorithm to use.  'sha256' is the standard choice:
#   • Produces a 64-character hexadecimal fingerprint.
#   • Extremely collision-resistant (two files sharing a hash is practically impossible).
#   • Fast enough for large files when read in chunks.
HASH_ALGORITHM = "sha256"

# File reading chunk size (bytes).
# 65 536 bytes = 64 KB — a balanced value:
#   • Small enough to keep memory usage flat even for multi-GB files.
#   • Large enough to avoid excessive system-call overhead.
CHUNK_SIZE = 65_536   # 64 KB

# ── Directory paths ─────────────────────────────────────────────────────────────

# Root directory of the project (the folder that contains this config.py file).
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 'data/' — stores baseline.json and last_alerts.json.
# IMPORTANT: This folder must NEVER be inside the user's monitored directory,
# otherwise the application would detect its own files as new/modified entries.
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

# 'logs/' — stores fim.log.
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# ── File paths ──────────────────────────────────────────────────────────────────

# baseline.json — the reference snapshot created when the user runs Option 1.
BASELINE_PATH = os.path.join(DATA_DIR, "baseline.json")

# last_alerts.json — the most recent scan result, written after every Option 2 run.
ALERTS_PATH   = os.path.join(DATA_DIR, "last_alerts.json")

# fim.log — append-only log file that records every significant application event.
LOG_PATH      = os.path.join(LOGS_DIR, "fim.log")

# ── Logging settings ────────────────────────────────────────────────────────────

# Log level written to fim.log.
# DEBUG   → everything (verbose, good during development)
# INFO    → normal operational messages
# WARNING → something unexpected but non-fatal
# ERROR   → something failed
LOG_LEVEL = "INFO"

# Format for each log line:
# Example output:  2026-11-16 10:30:00 | INFO     | Baseline created — 12 file(s) recorded.
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"

# Timestamp format used inside log lines.
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
