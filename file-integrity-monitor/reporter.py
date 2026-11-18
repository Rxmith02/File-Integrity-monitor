"""
reporter.py — Security Alert Reporter
=======================================
Formats and prints the integrity scan results in a clear,
color-coded layout.

Design rule: ALL display logic lives here.
monitor.py detects changes; reporter.py shows them.
Keeping them separate means you can change the UI without
touching the detection logic, and vice versa.
"""

import logging

from monitor import has_any_changes, count_changes

logger = logging.getLogger(__name__)

# ── ANSI color codes ──────────────────────────────────────────────────────────
# Work on Windows 10+ (cmd / PowerShell with virtual terminal sequences),
# macOS, and Linux. No third-party library needed.

RED    = "\033[91m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"   # Reset all formatting back to terminal default


# ── Public function ───────────────────────────────────────────────────────────

def display_report(changes, scanned_at=None, monitored_directory=""):
    """
    Print a formatted integrity report with color-coded severity alerts.

    Sections printed only when the corresponding list is non-empty:
      [HIGH]   RED    -- Modified files  (content changed -- possible tampering)
      [HIGH]   YELLOW -- Deleted files   (file removed    -- possible tampering)
      [MEDIUM] GREEN  -- New files       (file created    -- investigate intent)
      [INFO]   GREEN  -- All-clear       (no changes detected)

    Args:
        changes              (dict): Output from monitor.detect_changes(),
                                     with keys 'modified', 'deleted', 'new'.
        scanned_at           (str):  Timestamp of the scan (optional).
        monitored_directory  (str):  Path of the scanned folder (optional).
    """
    _print_header(scanned_at, monitored_directory)

    # ── All-clear path ────────────────────────────────────────────────────────
    if not has_any_changes(changes):
        print(f"\n  {GREEN}[INFO] All files are intact. No changes detected.{RESET}\n")
        logger.info("Scan report: no changes detected.")
        _print_footer()
        return

    # ── Modified files ────────────────────────────────────────────────────────
    # A hash mismatch means the file's content changed after baseline creation.
    # This is the most critical finding -- could indicate unauthorized tampering.
    modified = changes.get("modified", [])
    if modified:
        print(f"\n  {RED}{BOLD}[HIGH] MODIFIED FILES  ({len(modified)}){RESET}")
        print(f"  {'-' * 50}")
        print(f"  {RED}  Content changed after baseline was created.{RESET}")
        print(f"  {'-' * 50}")
        for path in modified:
            print(f"  {RED}  [~]  {path}{RESET}")
            logger.warning("MODIFIED : %s", path)

    # ── Deleted files ─────────────────────────────────────────────────────────
    # File was in the baseline but is gone now.
    deleted = changes.get("deleted", [])
    if deleted:
        print(f"\n  {YELLOW}{BOLD}[HIGH] DELETED FILES  ({len(deleted)}){RESET}")
        print(f"  {'-' * 50}")
        print(f"  {YELLOW}  Present at baseline time -- now missing.{RESET}")
        print(f"  {'-' * 50}")
        for path in deleted:
            print(f"  {YELLOW}  [x]  {path}{RESET}")
            logger.warning("DELETED  : %s", path)

    # ── New files ─────────────────────────────────────────────────────────────
    # File appeared after baseline -- could be benign or malware dropped.
    new = changes.get("new", [])
    if new:
        print(f"\n  {GREEN}{BOLD}[MEDIUM] NEW FILES  ({len(new)}){RESET}")
        print(f"  {'-' * 50}")
        print(f"  {GREEN}  Not present at baseline time -- investigate origin.{RESET}")
        print(f"  {'-' * 50}")
        for path in new:
            print(f"  {GREEN}  [+]  {path}{RESET}")
            logger.info("NEW FILE : %s", path)

    # ── Summary bar ───────────────────────────────────────────────────────────
    counts = count_changes(changes)
    print(f"\n  {'-' * 50}")
    print(
        f"  {BOLD}SUMMARY:{RESET}  "
        f"{RED}{counts['modified']} modified{RESET}  |  "
        f"{YELLOW}{counts['deleted']} deleted{RESET}  |  "
        f"{GREEN}{counts['new']} new{RESET}  |  "
        f"{BOLD}Total alerts: {counts['total']}{RESET}"
    )

    logger.info(
        "Report displayed -- modified: %d | deleted: %d | new: %d",
        counts["modified"], counts["deleted"], counts["new"]
    )

    _print_footer()


# ── Private helpers ───────────────────────────────────────────────────────────

def _print_header(scanned_at=None, monitored_directory=""):
    """Print the report's top border, title, and optional scan metadata."""
    print("\n" + "=" * 55)
    print(f"{BOLD}        FILE INTEGRITY REPORT{RESET}")
    print("=" * 55)
    if monitored_directory:
        display_dir = (monitored_directory[:45] + "...") \
                      if len(monitored_directory) > 48   \
                      else monitored_directory
        print(f"  Directory : {CYAN}{display_dir}{RESET}")
    if scanned_at:
        print(f"  Scanned   : {scanned_at}")
    print("=" * 55)


def _print_footer():
    """Print the report's bottom border."""
    print("=" * 55 + "\n")
