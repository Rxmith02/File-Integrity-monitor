# 🛡️ File Integrity Monitoring (FIM) System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Web%20UI-Flask-lightgrey?logo=flask)
![Tests](https://img.shields.io/badge/Tests-33%20Passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)
![SHA-256](https://img.shields.io/badge/Hashing-SHA--256-orange)

> A cybersecurity project that detects unauthorized changes to files using **SHA-256 cryptographic hashing**, with a **Flask web dashboard** and **33 automated unit tests**.

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/file-integrity-monitor.git
cd file-integrity-monitor

# 2. Install Flask (the only dependency)
pip install flask

# 3. Launch the web interface
python app.py

# 4. Open your browser at http://localhost:5000
```

Or use the terminal menu:
```bash
python main.py
```

---

## 📋 Table of Contents

1. [Project Introduction](#1-project-introduction)
2. [Problem Statement](#2-problem-statement)
3. [Project Objectives](#3-project-objectives)
4. [Technologies Used](#4-technologies-used)
5. [System Architecture](#5-system-architecture)
6. [Folder Structure](#6-folder-structure)
7. [How SHA-256 Works in This Project](#7-how-sha-256-works-in-this-project)
8. [How Baseline Creation Works](#8-how-baseline-creation-works)
9. [How File Modification Detection Works](#9-how-file-modification-detection-works)
10. [How New and Deleted Files Are Detected](#10-how-new-and-deleted-files-are-detected)
11. [Installation Instructions](#11-installation-instructions)
12. [Execution Instructions](#12-execution-instructions)
13. [Testing Instructions](#13-testing-instructions)
14. [Sample Output](#14-sample-output)
15. [Advantages](#15-advantages)
16. [Limitations](#16-limitations)
17. [Future Enhancements](#17-future-enhancements)

---

## 1. Project Introduction

The **File Integrity Monitoring System** is a command-line cybersecurity tool that detects unauthorized or unexpected changes to files within a monitored directory.

It works by computing a **SHA-256 cryptographic hash** (a unique digital fingerprint) for every file in a folder and saving this as a **baseline snapshot**. On subsequent scans, it recomputes hashes and compares them against the saved baseline — flagging any file that was modified, deleted, or newly created.

This concept is used in production security tools such as **Tripwire**, **OSSEC**, and **Wazuh**, and is a core technique in Security Operations Centre (SOC) environments.

---

## 2. Problem Statement

Organizations store sensitive data — employee records, financial reports, source code, configuration files. Attackers who gain access to a system often modify or delete these files to:

- Exfiltrate data quietly
- Plant backdoors or malware
- Cover their tracks by altering logs
- Tamper with software for malicious execution

Standard access controls (passwords, permissions) can be bypassed. Even after a breach, organizations may not know *which* files were touched or *when* the tampering occurred.

**File Integrity Monitoring solves this.** By maintaining a trusted baseline of original file fingerprints, any subsequent change — no matter how small — is immediately detectable.

---

## 3. Project Objectives

- Compute SHA-256 hashes for all files in a selected directory recursively.
- Save the original hashes as a baseline snapshot in JSON format.
- On demand, re-scan the directory and compare current hashes against the baseline.
- Classify and report:
  - **Modified files** — content changed (hash mismatch)
  - **Deleted files** — present in baseline, absent now
  - **New files** — absent from baseline, present now
  - **Unchanged files** — hash matches exactly
- Save scan results (alerts) for later review.
- Maintain an application log of all events.
- Handle errors gracefully (inaccessible files, corrupted baseline, etc.)

---

## 4. Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| `hashlib` | SHA-256 hash computation |
| `os` / `pathlib` | File and directory traversal |
| `json` | Baseline and alert storage |
| `datetime` | Timestamps for baseline and scan records |
| `logging` | Application event logging to `fim.log` |
| `unittest` | Automated test suite |

> **Zero third-party dependencies.** No `pip install` required.

---

## 5. System Architecture

This project follows a **modular architecture** — each file has one clearly defined responsibility.

```
main.py
  │
  ├── hasher.py      ← SHA-256 engine        (compute hashes)
  ├── baseline.py    ← JSON persistence       (save / load data)
  ├── monitor.py     ← Detection logic        (compare hashes)
  ├── reporter.py    ← Display engine         (format output)
  └── config.py      ← Central settings       (single source of truth)
```

### Data Flow — Option 2 (Scan for Changes)

```
User selects Option 2
        │
        ▼
load_baseline()          ← reads data/baseline.json
        │
        ▼
hash_folder(directory)   ← computes current SHA-256 hashes
        │
        ▼
detect_changes(          ← compares baseline vs current
    baseline_dict,
    current_dict
)
        │
        ▼
save_alerts(changes)     ← writes data/last_alerts.json
        │
        ▼
display_report(changes)  ← prints colour-coded terminal report
```

---

## 6. Folder Structure

```
file-integrity-monitor/
│
├── main.py               ← Entry point — run this file
├── config.py             ← All settings in one place
├── hasher.py             ← SHA-256 hashing engine
├── baseline.py           ← JSON save/load for baseline & alerts
├── monitor.py            ← Change detection logic (pure functions)
├── reporter.py           ← Formatted terminal output
│
├── data/
│   ├── baseline.json     ← Auto-generated hash snapshot
│   └── last_alerts.json  ← Auto-generated last scan result
│
├── logs/
│   └── fim.log           ← Auto-generated application log
│
├── tests/
│   ├── __init__.py
│   ├── test_hasher.py    ← 11 tests for hashing engine
│   ├── test_baseline.py  ← 10 tests for JSON storage
│   └── test_monitor.py   ← 12 tests for detection logic
│
├── sample_data/          ← Demo folder for real-world walkthrough
│   ├── employee.txt
│   ├── confidential.txt
│   └── report.txt
│
├── README.md
├── INTERVIEW_PREPARATION.md
├── requirements.txt
└── .gitignore
```

---

## 7. How SHA-256 Works in This Project

**SHA-256** (Secure Hash Algorithm 256-bit) is a one-way cryptographic function that converts any input (a file's contents) into a fixed-length 64-character hexadecimal string called a **digest** or **hash**.

### Key properties used in this project

| Property | What it means | Why it matters |
|----------|---------------|----------------|
| **Deterministic** | Same input → same output, always | Guarantees identical files produce identical hashes |
| **Avalanche effect** | 1 bit changed → ~50% of output bits flip | Even the tiniest edit is immediately detectable |
| **One-way (irreversible)** | Cannot reconstruct the original file from its hash | Safe to store and compare without exposing file contents |
| **Collision resistant** | Two different files sharing a hash is practically impossible | Comparison results are trustworthy |

### Example — avalanche effect

```
"Hello, World!"  →  dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f
"Hello, World?"  →  f16c3bb0532537acd5b2e418f2b1235b29181e35cffee7cc29d84de4a1d62e4d
```

One character changed (`!` → `?`). The entire 64-character hash is different.

### Implementation — chunk-based reading

```python
# From hasher.py
hasher = hashlib.new(HASH_ALGORITHM)   # sha256

with open(file_path, "rb") as f:
    chunk = f.read(CHUNK_SIZE)         # Read 64 KB at a time
    while chunk:
        hasher.update(chunk)           # Feed chunk into hasher
        chunk = f.read(CHUNK_SIZE)

return hasher.hexdigest()              # 64-character hex string
```

Reading in **64 KB chunks** (instead of loading the whole file) means the system works correctly even on files several gigabytes in size without running out of memory.

---

## 8. How Baseline Creation Works

**Option 1 — Create Initial Baseline**

1. The user enters the path of the folder to monitor.
2. `hash_folder()` calls `os.walk()` to visit every file recursively.
3. For each file, `hash_file()` computes its SHA-256 hash.
4. File paths are stored as **relative paths** (e.g. `employee.txt`, not `C:\full\path\employee.txt`) so the baseline is portable.
5. The result is saved to `data/baseline.json` as a JSON envelope:

```json
{
    "created_at": "2026-11-18 10:30:00",
    "monitored_directory": "C:\\Users\\User\\sample_data",
    "file_count": 3,
    "files": {
        "employee.txt":    "a3f1...",
        "confidential.txt":"b2e9...",
        "report.txt":      "c7d4..."
    }
}
```

> **Important:** The `data/` folder storing the baseline is located inside the project directory, not inside the monitored folder. This prevents the application from flagging its own baseline file as a "new file."

---

## 9. How File Modification Detection Works

**Option 2 — Scan for Changes**

When a file is modified after baseline creation:

1. The current scan computes a new SHA-256 hash for the file.
2. `detect_changes()` compares the current hash against the baseline hash.
3. If they differ → the file is classified as **MODIFIED**.

```python
# From monitor.py
for rel_path, original_hash in baseline_dict.items():
    if rel_path in current_dict:
        if current_dict[rel_path] != original_hash:
            changes["modified"].append(rel_path)   # hash mismatch = tampering
```

**Why this works:** SHA-256 is deterministic. If even one byte of the file changes, its hash changes completely. A matching hash guarantees the file is byte-for-byte identical to what was in the baseline.

---

## 10. How New and Deleted Files Are Detected

The `detect_changes()` function performs two passes over the data:

### Pass 1 — Walk the baseline (find modified + deleted)

```python
for rel_path, original_hash in baseline_dict.items():
    if rel_path not in current_dict:
        changes["deleted"].append(rel_path)       # was there, now gone
    elif current_dict[rel_path] != original_hash:
        changes["modified"].append(rel_path)      # hash changed
```

### Pass 2 — Walk the current scan (find new files)

```python
for rel_path in current_dict:
    if rel_path not in baseline_dict:
        changes["new"].append(rel_path)           # wasn't there before
```

This two-pass approach guarantees every possible change type is captured without missing any case.

---

## 11. Installation Instructions

### Prerequisites

- Python 3.8 or later
- Windows 10/11, macOS, or Linux

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/file-integrity-monitor.git
cd file-integrity-monitor

# 2. No pip install needed — zero external dependencies

# 3. Verify Python version
python --version
```

---

## 12. Execution Instructions

```bash
# Run from the project root directory
python main.py
```

You will see the main menu:

```
=======================================================
    FILE INTEGRITY MONITORING SYSTEM
    v1.0.0
=======================================================
  Baseline : d:\...\data\baseline.json
=======================================================

  MENU
  ------------------------------------------------
  [ 1 ]  Create Initial Baseline
  [ 2 ]  Scan Folder & Detect Changes
  [ 3 ]  View Last Scan Alerts
  [ 4 ]  Update Baseline  (overwrites existing)
  [ 5 ]  Exit
  ------------------------------------------------
```

### Typical workflow

```
Step 1 → Select Option 1 → Enter folder path → Baseline created
Step 2 → Make changes to files in that folder
Step 3 → Select Option 2 → Enter same folder path → Changes detected
Step 4 → Select Option 3 → Review alerts without re-scanning
Step 5 → Select Option 4 → Accept changes → Update baseline
```

---

## 13. Testing Instructions

```bash
# Run ALL tests (from the project root)
python -m unittest discover tests/ -v

# Run a single test file
python -m unittest tests/test_hasher.py -v
python -m unittest tests/test_baseline.py -v
python -m unittest tests/test_monitor.py -v
```

Expected output: all tests pass with `OK`.

---

## 14. Sample Output

### Baseline Created

```
  Scanning: C:\Users\User\sample_data
  Done — 3 file(s) hashed, 0 skipped.

  [+] Baseline saved >> ...\data\baseline.json
      Files recorded : 3
      Created at     : 2026-11-18 10:30:00

  Baseline created successfully!
```

### Scan Report (after modifications)

```
=======================================================
        FILE INTEGRITY REPORT
=======================================================
  Directory : C:\Users\User\sample_data
  Scanned   : 2026-11-18 10:35:00
=======================================================

  [HIGH] MODIFIED FILES  (1)
  --------------------------------------------------
    [~]  employee.txt

  [HIGH] DELETED FILES  (1)
  --------------------------------------------------
    [x]  confidential.txt

  [MEDIUM] NEW FILES  (1)
  --------------------------------------------------
    [+]  unknown.txt

  --------------------------------------------------
  SUMMARY:  1 modified  |  1 deleted  |  1 new  |  Total alerts: 3
=======================================================
```

### All-clear (no changes)

```
  [INFO] All files are intact. No changes detected.
```

---

## 15. Advantages

| Advantage | Detail |
|-----------|--------|
| **Zero dependencies** | Runs on any Python 3.8+ installation without pip install |
| **SHA-256 reliability** | Practically impossible to forge a matching hash accidentally |
| **Portable baselines** | Relative paths mean baselines survive folder moves |
| **Chunk-based hashing** | Works on files of any size without memory issues |
| **Modular code** | Each module has one job — easy to understand and modify |
| **Persistent alerts** | Alerts saved to JSON — review without re-scanning |
| **Full logging** | Every event recorded in fim.log for audit purposes |
| **Graceful error handling** | Inaccessible files are skipped with warnings, not crashes |

---

## 16. Limitations

> These are important to understand and disclose — especially in an interview.

1. **On-demand only, not real-time.**  
   This system scans when you tell it to. It does not monitor files continuously. A file could be modified and restored between scans without detection.

2. **Baseline tampering risk.**  
   If an attacker also modifies `data/baseline.json`, the comparison becomes invalid. The baseline itself is not cryptographically protected in this implementation.

3. **No encryption.**  
   SHA-256 produces hashes, not encryption. The file contents are not protected — only their integrity can be verified.

4. **No access control.**  
   Anyone who can run the script can also overwrite the baseline (Option 4). In production, baseline updates should require elevated privileges.

5. **SHA-256 is not infallible (theoretical).**  
   No known practical collisions exist for SHA-256, but it is theoretically not 100% collision-free. For ultra-high security, SHA-3 or BLAKE3 can be substituted.

---

## 17. Future Enhancements

| Enhancement | Description |
|------------|-------------|
| **Real-time monitoring** | Use `watchdog` library to trigger scans on file system events |
| **HMAC-signed baseline** | Sign `baseline.json` with a secret key to detect tampering |
| **Email / webhook alerts** | Send notifications when changes are detected |
| **SIEM integration** | Export alerts in JSON/CEF format for tools like Splunk or ELK |
| **Scheduled scans** | Run automatic scans using Windows Task Scheduler or cron |
| **File recovery info** | Show which baseline hash a modified file should be restored to |
| **Whitelist patterns** | Ignore expected changes (e.g. `.log` files) using regex rules |
| **GUI interface** | Add a simple tkinter or web-based dashboard |
| **Multi-directory support** | Monitor multiple directories in a single baseline |
| **Database backend** | Replace JSON with SQLite for faster lookups on large file sets |

---

*Built with Python 3 — zero third-party dependencies — suitable for Windows 10/11, macOS, and Linux.*
