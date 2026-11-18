"""
hasher.py — File Hashing Engine
================================
Calculates SHA-256 hashes for individual files and entire folders.
This module only handles hashing — no storage, no menus.

Configuration values (CHUNK_SIZE, HASH_ALGORITHM) are imported from
config.py so they never need to be changed here directly.
"""

import hashlib
import logging
import os

from config import CHUNK_SIZE, HASH_ALGORITHM

# Module-level logger — messages go to fim.log via the root logger
# configured in main.py.  Using __name__ keeps log entries clearly
# labelled as coming from 'hasher'.
logger = logging.getLogger(__name__)


def hash_file(file_path):
    """
    Calculate the SHA-256 hash of a single file.

    Reads the file in CHUNK_SIZE-byte (64 KB) chunks so large files
    are handled efficiently without loading everything into memory.

    Args:
        file_path (str): Absolute path to the file.

    Returns:
        str:  SHA-256 hex-digest string (64 hex characters), or
        None: if the file cannot be read (logs the reason).
    """
    # hashlib.new() lets us pick the algorithm from config (sha256, sha512, etc.)
    hasher = hashlib.new(HASH_ALGORITHM)

    try:
        with open(file_path, "rb") as f:
            # Read the file in CHUNK_SIZE pieces — never loads the whole file at once
            chunk = f.read(CHUNK_SIZE)
            while chunk:
                hasher.update(chunk)       # Feed each chunk into the hasher
                chunk = f.read(CHUNK_SIZE)

        return hasher.hexdigest()          # Return final hash as 64-char hex string

    except PermissionError:
        msg = f"Permission denied — skipped: {file_path}"
        print(f"    [!] {msg}")
        logger.warning(msg)
        return None

    except FileNotFoundError:
        msg = f"File not found — skipped: {file_path}"
        print(f"    [!] {msg}")
        logger.warning(msg)
        return None

    except OSError as error:
        # Catch-all for other I/O problems (locked files, broken links, etc.)
        msg = f"Cannot read '{file_path}': {error}"
        print(f"    [!] {msg}")
        logger.error(msg)
        return None


def hash_folder(folder_path, exclude_paths=None):
    """
    Recursively scan a folder and compute SHA-256 hashes for every file.

    Uses os.walk() to descend into all subfolders automatically.
    Keys in the returned dict are *relative* paths so the baseline
    remains valid even if the monitored folder is moved or renamed.

    Args:
        folder_path   (str):        Absolute path to the folder to scan.
        exclude_paths (set | None): Absolute paths to skip entirely.
                                    Pass the DATA_DIR and LOGS_DIR here when
                                    they happen to be inside the monitored folder
                                    so the app never flags its own files.

    Returns:
        dict: { relative_file_path (str): sha256_hash (str) }
              Files that raised errors are excluded from the result.
    """
    hash_dict     = {}
    exclude_paths = exclude_paths or set()

    # Validate the folder before starting
    if not os.path.isdir(folder_path):
        msg = f"Folder not found: {folder_path}"
        print(f"\n  [!] {msg}")
        logger.error(msg)
        return hash_dict

    logger.info("Scan started — directory: %s", folder_path)
    print(f"\n  Scanning: {folder_path}")

    file_count  = 0   # Successfully hashed files
    error_count = 0   # Files that could not be read

    # os.walk() yields (current_dir, subdirs, filenames) for every folder
    for root, dirs, files in os.walk(folder_path):
        dirs.sort()   # Sort so traversal order is consistent across runs
        files.sort()

        # Remove excluded directories in-place so os.walk() won't descend into them.
        # This prevents the app from scanning its own data/ or logs/ folder.
        dirs[:] = [
            d for d in dirs
            if os.path.abspath(os.path.join(root, d)) not in exclude_paths
        ]

        for filename in files:
            abs_path = os.path.join(root, filename)

            # Skip files whose absolute path is in the exclusion list
            if os.path.abspath(abs_path) in exclude_paths:
                continue

            # Relative path keeps the baseline folder-portable
            rel_path = os.path.relpath(abs_path, folder_path)

            file_hash = hash_file(abs_path)

            if file_hash is not None:
                hash_dict[rel_path] = file_hash
                file_count += 1
            else:
                error_count += 1

    # Summary line after the scan
    summary = f"Scan complete — {file_count} file(s) hashed, {error_count} skipped."
    print(f"  {summary}")
    logger.info(summary)

    return hash_dict
