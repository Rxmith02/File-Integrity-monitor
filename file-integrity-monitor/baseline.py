"""
baseline.py — Baseline Storage Manager
=======================================
Saves and loads the JSON hash baseline, and persists the last scan's
alerts so they can be viewed later without re-scanning.

JSON structure stored in baseline.json:
{
    "created_at"          : "2026-11-16 10:30:00",
    "monitored_directory" : "C:\\Users\\User\\Documents\\TestFolder",
    "file_count"          : 3,
    "files": {
        "employee.txt"      : "abc123...",
        "confidential.txt"  : "def456...",
        "report.txt"        : "ghi789..."
    }
}

All file paths are imported from config.py — nothing is hardcoded here.
"""

import json
import logging
import os
from datetime import datetime

from config import BASELINE_PATH, ALERTS_PATH, DATA_DIR

logger = logging.getLogger(__name__)

# Backward-compatible aliases (main.py imports these names)
DEFAULT_BASELINE_PATH = BASELINE_PATH
DEFAULT_ALERTS_PATH   = ALERTS_PATH


# ── Helper ────────────────────────────────────────────────────────────────────

def _ensure_data_dir():
    """Create the data/ directory if it does not already exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


# ── Baseline functions ────────────────────────────────────────────────────────

def save_baseline(hash_dict, monitored_directory="", baseline_path=BASELINE_PATH):
    """
    Write the hash dictionary to a JSON file (the baseline snapshot).

    The JSON envelope includes a timestamp and the monitored directory path
    so you can tell at a glance when the baseline was created and for which folder.

    Args:
        hash_dict             (dict): { relative_path: sha256_hash }
        monitored_directory   (str):  The folder that was scanned.
        baseline_path         (str):  Destination file path.

    Returns:
        bool: True on success, False on failure.
    """
    _ensure_data_dir()

    # Wrap the raw hash dict in a metadata envelope
    baseline_data = {
        "created_at"          : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitored_directory" : monitored_directory,
        "file_count"          : len(hash_dict),
        "files"               : hash_dict        # { relative_path: sha256_hash }
    }

    try:
        with open(baseline_path, "w") as f:
            # indent=4 makes the JSON human-readable in any text editor
            json.dump(baseline_data, f, indent=4)

        msg = (f"Baseline saved — {len(hash_dict)} file(s) recorded "
               f"[{monitored_directory}]")
        print(f"\n  [+] Baseline saved >> {baseline_path}")
        print(f"      Files recorded : {len(hash_dict)}")
        print(f"      Created at     : {baseline_data['created_at']}")
        logger.info(msg)
        return True

    except OSError as error:
        msg = f"Could not save baseline: {error}"
        print(f"\n  [!] {msg}")
        logger.error(msg)
        return False


def load_baseline(baseline_path=BASELINE_PATH):
    """
    Read an existing baseline from its JSON file.

    Handles both the NEW envelope format (with 'files' key and metadata)
    and the OLD flat format (direct dict of path → hash) for compatibility.

    Args:
        baseline_path (str): Path to the baseline JSON file.

    Returns:
        tuple: (hash_dict, metadata) where
               hash_dict (dict) is { relative_path: sha256_hash },
               metadata  (dict) holds created_at, monitored_directory, file_count.
               Returns (None, None) if the file is missing or unreadable.
    """
    if not os.path.isfile(baseline_path):
        print("\n  [!] No baseline found. Create one first (Option 1).")
        logger.warning("Baseline not found at: %s", baseline_path)
        return None, None

    try:
        with open(baseline_path, "r") as f:
            data = json.load(f)

        # ── Detect format ──────────────────────────────────────────────────
        # New format has a 'files' key; old flat format does not.
        if "files" in data:
            hash_dict = data["files"]
            metadata  = {
                "created_at"          : data.get("created_at", "unknown"),
                "monitored_directory" : data.get("monitored_directory", "unknown"),
                "file_count"          : data.get("file_count", len(hash_dict)),
            }
        else:
            # Old flat format — treat the whole dict as the hash map
            hash_dict = data
            metadata  = {
                "created_at"          : "unknown",
                "monitored_directory" : "unknown",
                "file_count"          : len(hash_dict),
            }

        logger.info(
            "Baseline loaded — %d file(s) on record. Created: %s",
            len(hash_dict), metadata["created_at"]
        )
        print(f"\n  [+] Baseline loaded — {len(hash_dict)} file(s) on record.")
        print(f"      Created at     : {metadata['created_at']}")
        print(f"      Directory      : {metadata['monitored_directory']}")
        return hash_dict, metadata

    except json.JSONDecodeError:
        msg = "Baseline file is corrupted. Recreate it (Option 1)."
        print(f"\n  [!] {msg}")
        logger.error(msg)
        return None, None

    except OSError as error:
        msg = f"Could not load baseline: {error}"
        print(f"\n  [!] {msg}")
        logger.error(msg)
        return None, None


# ── Alert-persistence functions ───────────────────────────────────────────────

def save_alerts(changes, monitored_directory="", alerts_path=ALERTS_PATH):
    """
    Persist the most recent scan's change report to a JSON file.

    The alerts file mirrors the baseline format — it includes a timestamp
    so you know when the last scan ran.

    Args:
        changes              (dict): Output from monitor.detect_changes().
        monitored_directory  (str):  Folder that was scanned.
        alerts_path          (str):  Destination file path.
    """
    _ensure_data_dir()

    alert_data = {
        "scanned_at"          : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitored_directory" : monitored_directory,
        "changes"             : changes
    }

    try:
        with open(alerts_path, "w") as f:
            json.dump(alert_data, f, indent=4)
        logger.info("Alerts saved — %s", alerts_path)
    except OSError as error:
        msg = f"Could not persist alerts: {error}"
        print(f"\n  [!] {msg}")
        logger.error(msg)


def load_alerts(alerts_path=ALERTS_PATH):
    """
    Load the most recently saved scan results from file.

    Returns:
        tuple: (changes_dict, metadata) or (None, None) if unavailable.
    """
    if not os.path.isfile(alerts_path):
        return None, None

    try:
        with open(alerts_path, "r") as f:
            data = json.load(f)

        # Support both new envelope format and legacy flat format
        if "changes" in data:
            changes  = data["changes"]
            metadata = {
                "scanned_at"          : data.get("scanned_at", "unknown"),
                "monitored_directory" : data.get("monitored_directory", "unknown"),
            }
        else:
            changes  = data
            metadata = {"scanned_at": "unknown", "monitored_directory": "unknown"}

        return changes, metadata

    except (json.JSONDecodeError, OSError):
        return None, None   # Treat corrupted file same as missing
