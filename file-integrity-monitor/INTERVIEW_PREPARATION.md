# 🎯 Interview Preparation Guide
## File Integrity Monitoring System — Python Cybersecurity Project

> Use this document to confidently explain every aspect of your project during a technical interview.  
> All answers are written in natural, conversational English — the way you would actually speak.

---

## SECTION 1 — Project Fundamentals

---

**Q: What is File Integrity Monitoring?**

File Integrity Monitoring, or FIM, is a security technique that detects unauthorized or unexpected changes to files on a system. It works by recording a "fingerprint" of every file when the system is in a known-good state — this is called the baseline. Later, when you run a scan, it recomputes those fingerprints and compares them to the baseline. Any file whose fingerprint has changed gets flagged immediately.

It's used in production environments to detect malware, insider threats, accidental modifications, and configuration drift.

---

**Q: Why did you choose this project?**

I chose this project because it covers multiple core cybersecurity concepts in a single, practical tool — cryptographic hashing, data integrity, security monitoring, and incident detection. It's also something that exists in the real world: tools like Tripwire and OSSEC use the same fundamental approach. Building it from scratch helped me understand exactly how those professional tools work under the hood. It's a project I can explain confidently because I built every component myself.

---

**Q: What problem does it solve?**

It solves the problem of not knowing whether files have been tampered with. If an attacker gains access to a server and modifies a critical file — say, a configuration file, an executable, or a log — there's no built-in way to know that happened unless you're actively monitoring. This tool gives you that visibility. It answers the question: "Are my files exactly the same as when I last verified them?"

---

**Q: What is SHA-256?**

SHA-256 stands for Secure Hash Algorithm, 256-bit output. It's a cryptographic function that takes any input — a file, a string, anything — and produces a fixed-length output of exactly 64 hexadecimal characters. That output is called a hash or digest. The same input always produces the same output, but completely different inputs produce completely different outputs. You cannot reverse it — you cannot go from the hash back to the original file.

---

**Q: What is cryptographic hashing?**

Cryptographic hashing is the process of converting data into a fixed-length fingerprint using a one-way mathematical function. "One-way" means you can compute the hash from the data, but you cannot reconstruct the data from the hash. It's also deterministic — the same data always produces the same hash. And it has the avalanche effect — a tiny change in input causes a massive change in output. These properties make it perfect for detecting file tampering.

---

**Q: Why SHA-256 specifically?**

Several reasons. First, it's available in Python's built-in `hashlib` library — no external packages needed. Second, it's fast enough for practical use even on large files. Third, it's collision-resistant — no two different files have ever been shown to produce the same SHA-256 hash in practice. Fourth, it's widely trusted in the security industry and is used in TLS, digital signatures, and blockchain. For even higher security, one could switch to SHA-3 or BLAKE3, but SHA-256 is the right balance for this project.

---

**Q: What is a baseline?**

A baseline is a trusted reference snapshot. In this project, it's a JSON file — `baseline.json` — that stores the SHA-256 hash of every file in the monitored folder at a specific point in time. The idea is: at that moment, the system was in a known-good state. The baseline captures what "good" looks like so you can compare everything against it later.

---

**Q: What is a hash mismatch?**

A hash mismatch means the SHA-256 hash of a file computed today is different from the hash stored in the baseline. Since SHA-256 is deterministic, a mismatch can only happen for one reason: the file's content has changed. Even if the file name, size, and timestamp look normal, the hash will catch the change. That's the power of cryptographic hashing over simple metadata checks.

---

**Q: How does the project detect unauthorized modifications?**

When you run a scan, the system recomputes the SHA-256 hash of every file in the directory. It then compares each current hash against the hash stored in the baseline. If the hashes match, the file is intact. If they don't match, the file was modified. If a file exists in the baseline but is missing now, it was deleted. If a file exists now but wasn't in the baseline, it's a new file. All three cases are flagged with appropriate severity labels.

---

## SECTION 2 — Implementation

---

**Q: Explain the architecture.**

The project uses a modular architecture — six Python files, each with a single responsibility. `config.py` holds all settings. `hasher.py` computes SHA-256 hashes and can't do anything else. `baseline.py` only reads and writes JSON files. `monitor.py` only compares two dictionaries — it has no file I/O at all. `reporter.py` only handles display. And `main.py` is the controller that ties everything together and presents the menu. This separation means each module is easy to understand, test, and modify independently.

---

**Q: Explain every Python module.**

- **`config.py`** — The single source of truth for all settings: hash algorithm, chunk size, file paths, log level, app version. Any value that appears more than once in the codebase lives here.

- **`hasher.py`** — Contains `hash_file()` and `hash_folder()`. `hash_file()` opens a file in binary mode, reads it in 64 KB chunks, feeds each chunk to a SHA-256 hasher, and returns the final hex digest. `hash_folder()` uses `os.walk()` to visit every file recursively and builds a dictionary of `{relative_path: sha256_hash}`.

- **`baseline.py`** — Contains `save_baseline()`, `load_baseline()`, `save_alerts()`, `load_alerts()`. Saves hash dictionaries to JSON with metadata (timestamp, directory). Loads them back and validates the JSON structure. Returns `(None, None)` on errors instead of crashing.

- **`monitor.py`** — Contains `detect_changes()`, `has_any_changes()`, `count_changes()`. Takes two dictionaries — the baseline and the current scan — and classifies every difference into modified, deleted, or new. It has zero imports from other project modules, making it trivially testable.

- **`reporter.py`** — Contains `display_report()`. Formats the changes dictionary into a colour-coded terminal report with severity labels: `[HIGH]` for modified and deleted, `[MEDIUM]` for new files, `[INFO]` when nothing changed. Uses ANSI escape codes — no external library.

- **`main.py`** — The entry point. Sets up logging, displays the menu, calls the appropriate function for each menu choice, and handles unexpected input gracefully.

---

**Q: Explain the important functions.**

- **`hash_file(file_path)`** — Opens the file in binary mode (`"rb"`), reads in CHUNK_SIZE chunks, feeds each to `hashlib.new("sha256")`, returns a 64-character hex string or `None` on error.

- **`hash_folder(folder_path, exclude_paths)`** — Uses `os.walk()` to recurse into every subdirectory. Skips directories in `exclude_paths` by modifying `dirs` in-place. Returns `{relative_path: hash}`.

- **`detect_changes(baseline_dict, current_dict)`** — Two-pass comparison. Pass 1 iterates the baseline to find modified and deleted files. Pass 2 iterates the current dict to find new files. Returns `{modified: [], deleted: [], new: []}`.

- **`save_baseline(hash_dict, monitored_directory)`** — Wraps the hash dict in a JSON envelope with `created_at`, `monitored_directory`, and `file_count` metadata. Writes to `baseline.json` with `indent=4` for human readability.

- **`load_baseline()`** — Reads the JSON file, extracts the `files` key (new format) or treats the whole dict as a flat map (legacy format). Returns `(hash_dict, metadata)` as a tuple — or `(None, None)` if the file is missing or corrupted.

- **`setup_logging()`** — Configures the Python root logger with two handlers: a file handler writing INFO+ to `fim.log`, and a console handler writing WARNING+ to the terminal. All other modules use `logging.getLogger(__name__)` and inherit this configuration automatically.

---

**Q: Explain how the modules communicate.**

They communicate through function return values only — no global variables, no shared state. `main.py` calls `hash_folder()` and receives a dictionary. It passes that dictionary to `save_baseline()`. Later, it calls `load_baseline()` to get it back as a tuple, extracts the hash dict, passes it and the current dict to `detect_changes()`, receives a changes dictionary, and passes that to both `save_alerts()` and `display_report()`. Every module only knows about its direct inputs and outputs.

---

**Q: Explain how JSON is used.**

JSON is used for two files: `baseline.json` and `last_alerts.json`. Python's built-in `json` module handles both. `json.dump(data, file, indent=4)` writes the dictionary as a human-readable JSON file. `json.load(file)` reads it back. The JSON envelope structure includes metadata like the creation timestamp and monitored directory path alongside the actual file hashes, so anyone who opens the file in a text editor can understand what it contains.

---

**Q: Explain how files are scanned recursively.**

Python's `os.walk(folder_path)` function is the key. It yields a tuple of `(current_directory, list_of_subdirectories, list_of_files)` for every directory it visits, automatically descending into subdirectories. We sort `dirs` in-place before each iteration to ensure consistent ordering across scans. We also modify `dirs` in-place to remove excluded directories — for example, `data/` and `logs/` — so `os.walk()` never descends into those folders.

---

**Q: Explain how the system handles errors.**

The system uses Python's `try-except` blocks to catch three main error types: `PermissionError` (can't read the file), `FileNotFoundError` (file disappeared during scan), and `OSError` (all other I/O errors). When any of these occur, `hash_file()` returns `None` and the file is excluded from the hash dictionary — not silently classified as deleted. This distinction matters: a file that cannot be read is different from a file that was deliberately removed. All errors are logged to `fim.log` and printed to the terminal with a `[!]` warning.

---

**Q: Explain the complete execution flow.**

1. User runs `python main.py`.
2. `setup_logging()` creates the `logs/` directory and configures handlers.
3. The main menu loop starts.
4. User selects Option 1 (Create Baseline):
   - `get_folder_path()` validates the entered path.
   - `hash_folder()` recursively hashes every file.
   - `save_baseline()` writes `baseline.json` with metadata.
5. User makes changes to files in the folder.
6. User selects Option 2 (Scan):
   - `load_baseline()` reads `baseline.json` → returns `(hash_dict, metadata)`.
   - `hash_folder()` recomputes current hashes.
   - `detect_changes(baseline_dict, current_dict)` classifies every difference.
   - `save_alerts(changes)` writes `last_alerts.json`.
   - `display_report(changes)` prints the colour-coded report.
7. User selects Option 3 (View Alerts):
   - `load_alerts()` reads `last_alerts.json` → no re-scan needed.
   - `display_report()` shows the saved report.

---

## SECTION 3 — Cybersecurity Concepts

---

**Q: What is the CIA Triad?**

The CIA Triad is the foundational model of information security. It stands for Confidentiality, Integrity, and Availability.

- **Confidentiality** means only authorized people can access sensitive data (encryption, access control).
- **Integrity** means data is accurate and has not been tampered with (hashing, digital signatures).
- **Availability** means systems and data are accessible when needed (redundancy, backups).

---

**Q: How does this project relate to Integrity?**

This project directly implements the **Integrity** component of the CIA Triad. Integrity in security means ensuring data has not been modified without authorization. SHA-256 hashing creates a verifiable fingerprint for every file. Any unauthorized modification changes the fingerprint. The comparison between the stored baseline and the current scan is precisely an integrity check — confirming that data remains exactly as it was when the baseline was established.

---

**Q: What is data tampering?**

Data tampering is the unauthorized modification of data — either by an external attacker, a malicious insider, or malware. It includes editing file contents, deleting records, injecting malicious code into executables, or altering log files to hide activity. This project detects tampering by comparing file hashes before and after, making it immediately visible when any file has been altered.

---

**Q: What is file monitoring?**

File monitoring is the practice of continuously or periodically observing files and directories for any changes — creation, modification, deletion, or access. It's a key component of host-based intrusion detection systems (HIDS). This project implements on-demand file monitoring using cryptographic hashing rather than real-time event monitoring.

---

**Q: What is the difference between hashing and encryption?**

They serve completely different purposes. **Hashing** is a one-way process — you take data, compute a fixed-length digest, and you cannot reverse it. It's used for verification, not secrecy. **Encryption** is a two-way process — you encrypt data with a key, and someone with the right key can decrypt it back to the original. It's used to protect confidentiality. In this project, we use hashing to verify that files haven't changed — we're not trying to keep the files secret.

---

**Q: Can two different files have the same hash? (Collision)**

Theoretically yes — this is called a collision. In practice, no collision has ever been found for SHA-256. The number of possible SHA-256 outputs is 2²⁵⁶ — a number astronomically larger than the number of atoms in the observable universe. The probability of accidentally producing two files with the same SHA-256 hash is essentially zero. So for all practical purposes in a FIM system, a matching hash means matching content.

---

**Q: Can SHA-256 be reversed?**

No. SHA-256 is specifically designed to be a one-way function. This means: given a hash, it is computationally infeasible to find any input that produces that hash. The only known practical attack is a brute-force preimage attack, which is computationally infeasible for SHA-256 due to its 256-bit output space.

---

**Q: Does hashing prevent file modification?**

No. Hashing does not prevent anything — it only detects changes after they have occurred. A file can still be modified at any time. The hash tells you that a modification happened when you next run a scan. Prevention requires access controls, file permissions, and write protection. This system is a detective control, not a preventive one.

---

**Q: What are the limitations of this project?**

1. **On-demand only** — not real-time. Changes between scans are undetected until the next scan.
2. **Baseline tampering** — if an attacker modifies both the file and the baseline, detection is bypassed.
3. **No prevention** — only detection after the fact.
4. **No baseline signing** — the baseline itself is not cryptographically authenticated.
5. **Single directory scope** — monitors one directory per session.

---

**Q: How is FIM useful in a SOC environment?**

In a Security Operations Centre, FIM is used to:
- Detect malware that modifies system executables or configuration files.
- Identify when attackers attempt to tamper with logs to cover their tracks.
- Fulfil compliance requirements — PCI-DSS, HIPAA, and SOX all mandate file integrity monitoring for certain system files.
- Provide forensic evidence after a breach — which files were touched and when.
- Trigger automated incident response workflows when critical files change.

---

## SECTION 4 — Advanced Follow-Up Questions

---

**Q: What if someone modifies the baseline?**

This is the fundamental limitation of any FIM system where the baseline is stored locally without protection. If an attacker has sufficient access to modify monitored files, they may also modify the baseline — making the tampering undetectable. 

The industry solution is to: (1) store the baseline on a separate, read-only or network-isolated system, (2) sign the baseline with an HMAC or digital signature using a secret key only the security team has, or (3) use a database with write-once, audit-logged entries.

For this project, I would explain this limitation honestly and propose HMAC signing as the next improvement.

---

**Q: What if a file changes while the scan is running?**

This is the TOCTOU problem — Time-Of-Check vs Time-Of-Use. If a file is modified between the moment `os.walk()` lists it and the moment `hash_file()` reads it, the computed hash reflects the modified version. In practice, for a small directory scanned quickly, this is rare. The current code handles the most likely case: if a file disappears entirely between listing and reading, `FileNotFoundError` is caught gracefully and the file is excluded from the current scan — not misclassified as deleted.

---

**Q: What happens if a file is inaccessible?**

`hash_file()` catches `PermissionError` and `OSError`, logs the error, prints a warning, and returns `None`. `hash_folder()` checks whether the return value is `None` before adding to the hash dictionary. Files that couldn't be read are simply excluded from the current scan result — they appear in neither the modified nor deleted lists. This prevents false positives. The error is recorded in `fim.log` for investigation.

---

**Q: How would you improve this project?**

Several ways, in order of priority:

1. **HMAC-sign the baseline** — prevents undetected baseline tampering.
2. **Real-time monitoring** — use Python's `watchdog` library to trigger scans on file system events instead of waiting for the user.
3. **Scheduled scans** — integrate with Windows Task Scheduler or cron for automatic periodic checks.
4. **Alert notifications** — send email or webhook alerts when critical changes are detected.
5. **Whitelist/ignore patterns** — skip files expected to change regularly (`.log`, `.tmp`) to reduce false positives.
6. **SQLite backend** — replace JSON with a database for better performance on large file sets.

---

**Q: How would you implement real-time monitoring?**

I would use the Python `watchdog` library, which wraps the operating system's native file system event APIs — `inotify` on Linux, `FSEvents` on macOS, `ReadDirectoryChangesW` on Windows. You define an event handler class with methods like `on_modified`, `on_created`, `on_deleted`, and an `Observer` thread calls your handler whenever the OS notifies it of a file system event. This is event-driven rather than polling — far more efficient and immediate than periodic scanning.

---

**Q: How could this system be integrated with a SIEM?**

A SIEM (Security Information and Event Management system) like Splunk, IBM QRadar, or the ELK Stack ingests log data from multiple sources and correlates events. Integration options:

1. **Log forwarding** — configure `fim.log` to be picked up by the SIEM's log collector agent (e.g. Splunk Universal Forwarder, Filebeat).
2. **JSON output** — the `last_alerts.json` file is already in JSON format and can be ingested directly.
3. **CEF/Syslog output** — add a reporter that outputs alerts in Common Event Format over syslog, which all major SIEMs natively consume.
4. **REST API** — post alerts to the SIEM's HTTP Event Collector (Splunk HEC) whenever a scan finds changes.

---

**Q: How would you reduce false positives?**

False positives are changes flagged as suspicious that are actually expected and legitimate. To reduce them:

1. **Whitelist patterns** — define regex patterns for files that change normally (e.g. `*.log`, `*.tmp`, `cache/*`) and skip them during comparison.
2. **Maintenance windows** — suppress alerts during known update or deployment periods.
3. **Change management integration** — if a change was approved in the ticketing system, automatically mark it as expected before scanning.
4. **Baseline update workflow** — after a legitimate software update, immediately update the baseline so the new file hashes become the trusted reference.
5. **Severity tuning** — classify changes in system executables as HIGH, changes in log files as LOW, so the analyst knows where to focus first.

---

*This guide covers everything you need to explain your project confidently in a technical interview — from fundamentals to advanced SOC-level questions.*
