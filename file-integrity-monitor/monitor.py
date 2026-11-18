"""
monitor.py — Change Detection Engine
======================================
Compares two hash dictionaries and classifies every difference into
one of three categories: modified, deleted, or new.

This module contains only pure logic — no file I/O, no printing.
That separation makes it easy to test and reason about independently.
"""

import logging

logger = logging.getLogger(__name__)


def detect_changes(baseline_dict, current_dict):
    """
    Compare baseline hashes with current hashes to find file changes.

    Three change types are detected:
      * modified — file exists in both snapshots but its hash differs
                   (the file content was altered)
      * deleted  — file was in the baseline but is missing now
                   (the file was removed)
      * new      — file exists now but was absent from the baseline
                   (a new file was created)

    Unchanged files (hash matches perfectly) are counted but not listed
    separately — their absence from all three lists implies they are intact.

    Args:
        baseline_dict (dict): Hash dict loaded from baseline.json  { path: hash }
        current_dict  (dict): Hash dict produced by the latest scan { path: hash }

    Returns:
        dict: {
            "modified": [sorted list of relative paths],
            "deleted":  [sorted list of relative paths],
            "new":      [sorted list of relative paths]
        }
    """
    changes = {
        "modified": [],
        "deleted":  [],
        "new":      []
    }

    # ── Pass 1: Examine every file recorded in the baseline ──────────────────
    for rel_path, original_hash in baseline_dict.items():

        if rel_path not in current_dict:
            # Present in baseline but absent now — the file was deleted
            changes["deleted"].append(rel_path)

        elif current_dict[rel_path] != original_hash:
            # Present in both but hash changed — content was modified
            changes["modified"].append(rel_path)

        # If hashes match, the file is intact — no action needed

    # ── Pass 2: Look for files that did not exist at baseline time ───────────
    for rel_path in current_dict:
        if rel_path not in baseline_dict:
            # Not in baseline but present now — a new file was created
            changes["new"].append(rel_path)

    # Sort each list so the report is always in a predictable, consistent order
    changes["modified"].sort()
    changes["deleted"].sort()
    changes["new"].sort()

    # Log a summary of what was found
    logger.info(
        "Change detection complete — modified: %d | deleted: %d | new: %d",
        len(changes["modified"]),
        len(changes["deleted"]),
        len(changes["new"]),
    )

    # Log each individual finding at DEBUG level for traceability
    for path in changes["modified"]:
        logger.debug("MODIFIED : %s", path)
    for path in changes["deleted"]:
        logger.debug("DELETED  : %s", path)
    for path in changes["new"]:
        logger.debug("NEW      : %s", path)

    return changes


def has_any_changes(changes):
    """
    Return True if at least one change was detected, False otherwise.

    Args:
        changes (dict): Output from detect_changes().

    Returns:
        bool
    """
    return any(len(file_list) > 0 for file_list in changes.values())


def count_changes(changes):
    """
    Return a summary dict with the count of each change type.

    Useful for displaying concise summaries in the terminal or log.

    Args:
        changes (dict): Output from detect_changes().

    Returns:
        dict: { "modified": int, "deleted": int, "new": int, "total": int }
    """
    modified = len(changes.get("modified", []))
    deleted  = len(changes.get("deleted",  []))
    new      = len(changes.get("new",      []))
    return {
        "modified": modified,
        "deleted" : deleted,
        "new"     : new,
        "total"   : modified + deleted + new
    }
