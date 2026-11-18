"""
main.py — Entry Point / CLI Menu
===================================
File Integrity Monitoring System  v1.0.0

This is the only file you need to run:
    python main.py

It presents a numbered menu, routes each choice to the correct function,
and sets up application-wide logging before anything else runs.

All heavy lifting is done by the other modules:
    config.py   — settings
    hasher.py   — SHA-256 engine
    baseline.py — JSON persistence
    monitor.py  — change detection logic
    reporter.py — formatted terminal output
"""

import logging
import os
import sys

from config import (
    APP_NAME, APP_VERSION,
    LOG_PATH, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT,
    LOGS_DIR, DATA_DIR, BASELINE_PATH,
)
from hasher    import hash_folder
from baseline  import (
    save_baseline, load_baseline,
    save_alerts,   load_alerts,
    DEFAULT_BASELINE_PATH,
)
from monitor   import detect_changes
from reporter  import display_report, CYAN, BOLD, GREEN, YELLOW, RED, RESET


# ── Logging setup ─────────────────────────────────────────────────────────────

def setup_logging():
    """
    Configure the root logger once at startup.

    Every module in the project calls logging.getLogger(__name__).
    Because they all inherit from the root logger configured here,
    a single call to setup_logging() captures log messages from
    hasher, baseline, monitor and reporter automatically.

    Log output goes to:
        • logs/fim.log  — persistent file (all messages)
        • Terminal      — WARNING and above only (keeps output clean)
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    # Translate the string level from config (e.g. "INFO") to the numeric constant
    numeric_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    # Root logger — must be set to the lowest level you want to capture
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)   # Accept everything; handlers filter

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # ── File handler — writes INFO and above to fim.log ───────────────────
    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)

    # ── Console handler — writes WARNING and above to terminal ────────────
    # We don't want INFO clutter in the menu UI; errors will still appear.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("=" * 60)
    logging.info("%s  v%s  —  Session started", APP_NAME, APP_VERSION)
    logging.info("=" * 60)


# ── Utility helpers ───────────────────────────────────────────────────────────

def clear_screen():
    """Clear the terminal so each menu view starts fresh."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    """Print the application title and current baseline location."""
    print("\n" + "=" * 55)
    print(f"{BOLD}    FILE INTEGRITY MONITORING SYSTEM{RESET}")
    print(f"    v{APP_VERSION}")
    print("=" * 55)
    print(f"  Baseline : {CYAN}{DEFAULT_BASELINE_PATH}{RESET}")
    print("=" * 55)


def get_folder_path():
    """
    Prompt the user for a folder path and validate it.

    Strips surrounding quotes because Windows sometimes adds them
    when a user drags a folder into the terminal window.

    Returns:
        str:  A valid, existing folder path.
        None: If the user pressed Enter without typing or the path
              does not point to a real folder.
    """
    print("\n  Enter the full path of the folder to monitor.")
    print("  (Press Enter to cancel)\n")
    folder = input("  Folder path: ").strip()

    if not folder:
        print("  Cancelled.")
        return None

    # Remove surrounding quotes added by Windows drag-and-drop
    folder = folder.strip('"').strip("'")

    if not os.path.isdir(folder):
        print(f"\n  {RED}[!] Path not found or is not a folder:{RESET}")
        print(f"      {folder}")
        logging.warning("Invalid folder path entered: %s", folder)
        return None

    return folder


def _get_exclude_paths():
    """
    Return absolute paths that should never be scanned.

    If the user monitors a parent folder that contains our data/ or logs/
    directory, we exclude those so the app never flags its own files.

    Returns:
        set of str: Absolute paths to skip during scanning.
    """
    return {
        os.path.abspath(DATA_DIR),
        os.path.abspath(LOGS_DIR),
    }


# ── Menu option handlers ──────────────────────────────────────────────────────

def option_create_baseline():
    """
    Option 1 — Create a fresh baseline from the chosen folder.

    Flow:
      1. Ask user for a folder path.
      2. Hash every file recursively (excluding data/ and logs/).
      3. Save hashes + metadata to data/baseline.json.
    """
    print(f"\n  {BOLD}[ 1 ] CREATE BASELINE{RESET}")
    logging.info("Option 1 selected — Create Baseline")

    folder = get_folder_path()
    if not folder:
        return

    print("\n  Calculating hashes — please wait...")
    hash_dict = hash_folder(folder, exclude_paths=_get_exclude_paths())

    if not hash_dict:
        print(f"\n  {YELLOW}[!] No readable files found. Baseline not saved.{RESET}")
        logging.warning("No readable files in: %s", folder)
        return

    if save_baseline(hash_dict, monitored_directory=folder):
        print(f"\n  {GREEN}Baseline created successfully!{RESET}")
        logging.info("Baseline created for: %s", folder)


def option_scan_changes():
    """
    Option 2 — Scan the folder and compare against the stored baseline.

    Flow:
      1. Load the existing baseline.
      2. Ask user for the folder path to scan.
      3. Hash current files.
      4. Compare current hashes against baseline.
      5. Save and display the results.
    """
    print(f"\n  {BOLD}[ 2 ] SCAN FOR CHANGES{RESET}")
    logging.info("Option 2 selected — Scan for Changes")

    # Load baseline; abort if it does not exist
    hash_dict, metadata = load_baseline()
    if hash_dict is None:
        return

    folder = get_folder_path()
    if not folder:
        return

    print("\n  Calculating current hashes — please wait...")
    current_dict = hash_folder(folder, exclude_paths=_get_exclude_paths())

    # Core comparison — returns {modified, deleted, new}
    changes = detect_changes(hash_dict, current_dict)

    # Persist results so Option 3 can display them without re-scanning
    save_alerts(changes, monitored_directory=folder)

    # Print the formatted report immediately
    display_report(changes, scanned_at=None, monitored_directory=folder)


def option_view_alerts():
    """
    Option 3 — Display alerts from the most recent scan.

    Reads the saved alerts file; no folder path is required.
    """
    print(f"\n  {BOLD}[ 3 ] VIEW LAST ALERTS{RESET}")
    logging.info("Option 3 selected — View Last Alerts")

    changes, metadata = load_alerts()

    if changes is None:
        print(f"\n  {YELLOW}[!] No scan results found.")
        print(f"      Run a scan first (Option 2).{RESET}\n")
        return

    # Show when and where the last scan ran
    if metadata:
        print(f"\n  Last scanned : {metadata.get('scanned_at', 'unknown')}")
        print(f"  Directory    : {metadata.get('monitored_directory', 'unknown')}")

    display_report(changes,
                   scanned_at=metadata.get("scanned_at") if metadata else None,
                   monitored_directory=metadata.get("monitored_directory", "") if metadata else "")


def option_update_baseline():
    """
    Option 4 — Overwrite the baseline with the current folder state.

    Requires explicit 'yes' confirmation to prevent accidental overwriting.
    Use this after you have reviewed and accepted detected changes.
    """
    print(f"\n  {BOLD}[ 4 ] UPDATE BASELINE{RESET}")
    logging.info("Option 4 selected — Update Baseline")

    print(f"\n  {YELLOW}[!] This will permanently overwrite the existing baseline.{RESET}")
    print(      "      Use this only after reviewing and accepting all changes.")
    print(      "      Updating the baseline sets the current file state as the")
    print(      "      new trusted reference — previous alerts will be invalidated.")

    confirm = input("\n  Type 'yes' to confirm, or anything else to cancel: ").strip().lower()

    if confirm != "yes":
        print(f"\n  {YELLOW}Update cancelled — baseline unchanged.{RESET}")
        logging.info("Baseline update cancelled by user.")
        return

    folder = get_folder_path()
    if not folder:
        return

    print("\n  Calculating hashes — please wait...")
    hash_dict = hash_folder(folder, exclude_paths=_get_exclude_paths())

    if not hash_dict:
        print(f"\n  {YELLOW}[!] No readable files found. Baseline not updated.{RESET}")
        return

    if save_baseline(hash_dict, monitored_directory=folder):
        print(f"\n  {GREEN}Baseline updated successfully!{RESET}")
        logging.info("Baseline updated for: %s", folder)


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    """
    Application entry point.

    Sets up logging first, then displays the menu in a loop and routes
    each user choice to the appropriate handler function.
    """
    setup_logging()

    while True:
        clear_screen()
        print_banner()

        print(f"\n  {BOLD}MENU{RESET}")
        print("  " + "-" * 48)
        print(f"  {CYAN}[ 1 ]{RESET}  Create Initial Baseline")
        print(f"  {CYAN}[ 2 ]{RESET}  Scan Folder & Detect Changes")
        print(f"  {CYAN}[ 3 ]{RESET}  View Last Scan Alerts")
        print(f"  {CYAN}[ 4 ]{RESET}  Update Baseline  {YELLOW}(overwrites existing){RESET}")
        print(f"  {CYAN}[ 5 ]{RESET}  Exit")
        print("  " + "-" * 48)

        choice = input("\n  Enter choice (1-5): ").strip()

        if choice == "1":
            option_create_baseline()
        elif choice == "2":
            option_scan_changes()
        elif choice == "3":
            option_view_alerts()
        elif choice == "4":
            option_update_baseline()
        elif choice == "5":
            logging.info("Application exited by user.")
            print(f"\n  {GREEN}Goodbye! Stay secure.{RESET}\n")
            sys.exit(0)
        else:
            print(f"\n  {YELLOW}[!] Invalid choice. Enter a number between 1 and 5.{RESET}")
            logging.warning("Invalid menu choice entered: %s", choice)

        # Pause before redrawing the menu so the user can read the output
        input("\n  Press Enter to return to the menu...")


# ── Script guard ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
