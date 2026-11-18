# 📘 COMPLETE TEACH-ME GUIDE
## File Integrity Monitoring System — Everything You Need to Know

> This guide teaches you the project from zero. Read it once a day for 2 days and you will be able to explain and demo it confidently in any interview.

---

# PART 1 — HOW TO RUN THE PROJECT

## Step A: Run the Web Interface (for demo & interview)

```
1. Open Command Prompt or PowerShell
2. Type this command:
   cd "d:\HCL PROJECTS\file-integrity-monitor"

3. Type this:
   python app.py

4. Open your browser and go to:
   http://localhost:5000

5. You will see the dark-themed dashboard.
   That's your web interface!
```

## Step B: Use the Demo Folder (sample_data)

Your project comes with a ready-made demo folder at:
```
d:\HCL PROJECTS\file-integrity-monitor\sample_data\
```

It contains 3 files:
- `employee.txt` — fake employee record
- `confidential.txt` — fake confidential document
- `report.txt` — fake monthly report

**Use this exact path in the browser when asked for a folder.**

## Step C: Run the Full Demo in 5 Steps

| Step | What to do in the browser |
|------|---------------------------|
| 1 | Enter `sample_data` path → Click "Create Baseline" |
| 2 | Manually open `employee.txt` in Notepad, change something, save |
| 3 | Manually delete `confidential.txt` |
| 4 | Create a new file `unknown.txt` anywhere in `sample_data` |
| 5 | Enter same path → Click "Run Integrity Scan" → See results |

You will see: `employee.txt` = MODIFIED (red), `confidential.txt` = DELETED (yellow), `unknown.txt` = NEW (green), `report.txt` = Unchanged (blue).

---

# PART 2 — WHAT EVERY FILE DOES (Simple Language)

Imagine the project as a security guard system for files. Each Python file is one guard with one job:

| File | Job | Simple explanation |
|------|-----|-------------------|
| `config.py` | Settings room | Holds all the settings in one place. Like a control panel. |
| `hasher.py` | Fingerprint taker | Opens every file and calculates its SHA-256 fingerprint (hash). |
| `baseline.py` | Filing cabinet | Saves all fingerprints to a JSON file. Loads them when needed. |
| `monitor.py` | Comparison engine | Compares old fingerprints (baseline) vs new fingerprints (scan). |
| `reporter.py` | Alarm system | Shows the results on screen in colored format. |
| `main.py` | Control room (CLI) | Shows a text menu. Run this if you want command-line use. |
| `app.py` | Web control room | Shows a web browser interface. Run this for the visual demo. |

---

# PART 3 — WHAT IS SHA-256 (Explain Like You Built It)

SHA-256 is a mathematical function. You give it a file, it gives you back exactly 64 characters — always. Think of it like a fingerprint for files.

**Three things you MUST remember:**

1. **Same file → Same hash, always.** If I hash `employee.txt` today and tomorrow without changing it, I always get the same 64 characters.

2. **Change one character → Completely different hash.** This is called the "avalanche effect." Even if you change one full stop to a comma, the entire 64-character hash changes completely.

3. **You cannot reverse it.** You cannot take the hash and get back the original file. It's a one-way function.

**How to explain it in one sentence:**
> *"SHA-256 creates a unique 64-character fingerprint for every file. If the file content changes even by one byte, the fingerprint completely changes — making tampering instantly detectable."*

**Live example you can show:**
```
"Hello, World!"  → dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f
"Hello, World?"  → f16c3bb0532537acd5b2e418f2b1235b29181e35cffee7cc29d84de4a1d62e4d
```
One character changed (`!` to `?`). Entire hash is different. This is what detects file tampering.

---

# PART 4 — HOW THE SYSTEM WORKS (Step by Step)

## When you click "Create Baseline":
1. You type the folder path.
2. The system calls `hash_folder()` in `hasher.py`.
3. `hash_folder()` uses `os.walk()` to visit every file in the folder.
4. For each file, it calls `hash_file()` which reads the file in 64 KB chunks and feeds it to `hashlib.sha256()`.
5. The result is a dictionary: `{"employee.txt": "abc123...", "report.txt": "xyz789..."}`
6. This dictionary is saved to `data/baseline.json` by `save_baseline()` in `baseline.py`.
7. The JSON also includes a timestamp and the folder path.

## When you click "Run Integrity Scan":
1. `load_baseline()` reads `data/baseline.json` and returns the saved hash dictionary.
2. `hash_folder()` runs again on the same folder — getting the CURRENT hashes.
3. `detect_changes()` in `monitor.py` compares the two dictionaries:
   - File in both but hash changed → **MODIFIED**
   - File in baseline but not in current → **DELETED**
   - File in current but not in baseline → **NEW**
   - File in both and hash matches → **UNCHANGED**
4. Results are saved to `data/last_alerts.json`.
5. The web page shows the results in colored cards.

---

# PART 5 — HOW TO EXPLAIN THE PROJECT IN AN INTERVIEW

## The 60-Second Pitch (Memorize This Word for Word)

> *"I built a File Integrity Monitoring System using Python. The idea came from real-world security tools like Tripwire and OSSEC that SOC teams use to detect unauthorized file changes.*
>
> *The system works by scanning a folder and calculating a SHA-256 hash — which is a 64-character cryptographic fingerprint — for every file. These fingerprints are saved as a baseline. Later, when you run a scan, the system recomputes every hash and compares it against the baseline. Any file whose hash doesn't match is immediately flagged as Modified, Deleted, or New.*
>
> *I built it in Python using only built-in libraries — hashlib for hashing, json for storage, logging for audit trails, and unittest for 33 automated tests. I also added a Flask web interface so the results are displayed visually in a browser. The project covers three core cybersecurity concepts: the Integrity pillar of the CIA Triad, cryptographic hashing, and security monitoring."*

---

## The Demo Script (What to Click and What to Say)

**Open your browser at http://localhost:5000**

**Say:** *"This is the dashboard. You can see the baseline status at the top. Currently there's no baseline created."*

**Action:** Type the `sample_data` folder path and click "Create Baseline"

**Say:** *"I'm pointing the system at this folder which has 3 files — an employee record, a confidential document, and a monthly report. The system is now calculating the SHA-256 hash of each file and saving them to baseline.json."*

**Show:** Point to the green success message and the file count.

**Say:** *"Now I'll simulate a real-world attack scenario. I'll modify the employee file, delete the confidential document, and drop a suspicious new file."*

**Action:** Open File Explorer, go to `sample_data`, open `employee.txt` in Notepad, change the salary, save it. Delete `confidential.txt`. Create a new file `unknown.txt`.

**Action:** Go back to browser, enter same path, click "Run Integrity Scan"

**Say:** *"The system has now recomputed the hashes and compared them against the baseline. Let me walk you through the results."*

**Point to RED section:** *"This is the modified file — employee.txt. The SHA-256 hash no longer matches the baseline. Even though the file name and size might look similar, the hash exposes the tampering."*

**Point to YELLOW section:** *"This is the deleted file — confidential.txt. It was recorded in the baseline but is now missing. Classic evidence destruction."*

**Point to GREEN section:** *"This is the new file — unknown.txt. It didn't exist when the baseline was created. This could be malware dropped by an attacker."*

**Point to BLUE section:** *"And this is report.txt — completely unchanged. The hash matches perfectly."*

**Say:** *"This is exactly the workflow a security analyst would follow in a SOC environment."*

---

# PART 6 — TOP INTERVIEW QUESTIONS AND YOUR ANSWERS

**Q: "Tell me about this project."**
→ Use the 60-second pitch above.

---

**Q: "Why did you use SHA-256 specifically?"**
→ *"SHA-256 is part of Python's built-in hashlib library — no external packages needed. It produces a 256-bit output, making collisions practically impossible. It's also widely trusted in the industry — it's used in TLS, digital signatures, and blockchain. It was the right balance of security and simplicity for this project."*

---

**Q: "What is the CIA Triad and how does your project relate to it?"**
→ *"The CIA Triad stands for Confidentiality, Integrity, and Availability — the three pillars of information security. My project directly addresses Integrity. Integrity means data hasn't been tampered with. By computing SHA-256 hashes and comparing them against a trusted baseline, I'm verifying that every file is exactly as it was when last verified."*

---

**Q: "How does os.walk() work?"**
→ *"os.walk() is a Python built-in that recursively traverses a directory. It yields a tuple of three things for every folder it visits: the current directory path, a list of subdirectory names, and a list of file names. I sort both lists before iterating to ensure consistent ordering across scans. I also modify the subdirectory list in-place to skip my own data/ and logs/ folders so the app never flags its own files."*

---

**Q: "Why did you read files in chunks instead of loading them fully?"**
→ *"If I load a 4 GB log file entirely into RAM, the program would crash with a memory error. Reading in 64 KB chunks feeds data to the SHA-256 hasher incrementally — the final hash is identical regardless of chunk size, but memory usage stays constant no matter how large the file is."*

---

**Q: "What is the baseline? Where is it stored?"**
→ *"The baseline is a JSON file — baseline.json — that stores the SHA-256 hash of every file in the monitored folder at a specific point in time. It's stored inside the project's data/ folder, which is kept separate from the monitored folder. If I stored it inside the monitored folder, the app would detect its own baseline file as a 'new file' every time, generating false alerts."*

---

**Q: "What if someone modifies both the file and the baseline?"**
→ *"That's the fundamental limitation of this implementation. If an attacker has enough access to modify both, detection is bypassed. The industry solution is to store the baseline on a separate read-only system, or sign it with an HMAC using a secret key that only the security team has. I would implement HMAC signing as the next improvement."*

---

**Q: "What happens if a file can't be read?"**
→ *"hash_file() uses a try-except block catching PermissionError, FileNotFoundError, and OSError. When any of these occur, it returns None and logs the error. hash_folder() checks the return value — if it's None, the file is excluded from the hash dictionary rather than being misclassified as deleted. This avoids false positives."*

---

**Q: "How did you test this project?"**
→ *"I wrote 33 automated unit tests using Python's built-in unittest module across three test files. test_hasher.py tests the hashing functions in isolation. test_baseline.py tests JSON save and load, including edge cases like corrupted files and missing files. test_monitor.py tests the detection logic with all scenarios — modified, deleted, new, unchanged, empty baselines, and sorted output. All 33 tests pass."*

---

**Q: "What is Flask and why did you use it?"**
→ *"Flask is a lightweight Python web framework. I used it to build a browser-based interface for the system. When you run python app.py, it starts a local web server on port 5000. The browser communicates with Flask using HTML forms — the form submits a POST request with the folder path, Flask calls the same Python functions as the CLI menu, and returns a rendered HTML page with the results. It makes the demo much more visual and professional."*

---

**Q: "Is this a real-time monitoring system?"**
→ *"No — this is an on-demand scanning system. You run it when you want to check. A real-time system would use something like Python's watchdog library, which listens to file system events from the OS. That would be my next enhancement. But for the core concept of FIM — hash-based integrity verification — the on-demand approach demonstrates all the fundamental principles."*

---

**Q: "How is FIM used in a SOC environment?"**
→ *"In a Security Operations Centre, FIM tools monitor critical system files — executables, configuration files, log files. If malware modifies a system binary or an attacker edits a log to hide their tracks, the FIM system immediately alerts the analyst. It's also required by compliance standards like PCI-DSS and HIPAA for specific files. Tools like Tripwire, OSSEC, and Wazuh do this at enterprise scale with real-time monitoring and SIEM integration."*

---

**Q: "Can you explain your code for hash_file()?"**
→ *"hash_file() takes a file path as input. It creates a new SHA-256 hasher using hashlib.new('sha256'). It opens the file in binary mode — 'rb' — because we need the raw bytes, not text. It then reads the file in 64 KB chunks in a while loop, calling hasher.update(chunk) for each chunk. After the loop, hasher.hexdigest() returns the final 64-character hex string. If any error occurs — permission denied, file not found, or any other IO error — it catches the exception, logs it, and returns None."*

---

# PART 7 — GITHUB PUSH GUIDE (Step by Step from Zero)

## Step 1: Check if Git is Installed

Open Command Prompt and type:
```
git --version
```

If you see `git version 2.x.x` → Git is installed. Skip to Step 3.
If you get an error → Go to Step 2.

## Step 2: Install Git

1. Go to: https://git-scm.com/download/win
2. Download and install (click Next → Next → Finish, all defaults are fine)
3. Restart Command Prompt
4. Run `git --version` again to confirm

## Step 3: Set Your Identity (One Time Only)

```
git config --global user.name "Your Full Name"
git config --global user.email "your.email@gmail.com"
```

Replace with your actual name and email.

## Step 4: Create a GitHub Account

1. Go to https://github.com
2. Click "Sign Up"
3. Create a free account with your email

## Step 5: Create a New Repository on GitHub

1. Click the **+** button at the top right → "New repository"
2. Repository name: `file-integrity-monitor`
3. Description: `File Integrity Monitoring System using Python and SHA-256 hashing`
4. Keep it **Public** (so interviewers can see it)
5. Do NOT check "Add a README file" (you already have one)
6. Click **Create repository**
7. GitHub will show you a URL like: `https://github.com/yourusername/file-integrity-monitor.git`
   **Copy this URL — you need it in Step 7.**

## Step 6: Initialize Git in Your Project Folder

Open Command Prompt and type:
```
cd "d:\HCL PROJECTS\file-integrity-monitor"
git init
git branch -M main
```

## Step 7: Connect to GitHub and Push

```
git add .
git commit -m "Initial commit: File Integrity Monitoring System with Flask web UI and 33 unit tests"
git remote add origin https://github.com/YOURUSERNAME/file-integrity-monitor.git
git push -u origin main
```

Replace `YOURUSERNAME` with your actual GitHub username.

## Step 8: Verify

Go to `https://github.com/YOURUSERNAME/file-integrity-monitor`

You should see all your files listed there with the README displayed below.

## If GitHub asks for a password:

GitHub no longer accepts plain passwords. Use a Personal Access Token:
1. GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name, check the `repo` checkbox, click Generate
4. Copy the token (it looks like `ghp_xxxx...`)
5. Use this token as your password when git asks

---

# PART 8 — WHAT TO SAY ON YOUR RESUME

**Project Title:** File Integrity Monitoring System using Python

**One-line description:**  
*A Python-based cybersecurity tool that detects unauthorized file modifications using SHA-256 cryptographic hashing, with a Flask web interface and 33 automated unit tests.*

**Tech stack line:**  
Python 3, hashlib, Flask, JSON, logging, unittest, Bootstrap 5, SHA-256, OS module

**Bullet points for resume:**
- Developed a File Integrity Monitoring (FIM) system that detects unauthorized modifications, deletions, and new file creation using SHA-256 cryptographic hashing
- Implemented chunk-based file reading (64 KB) to support large-file hashing without memory constraints
- Built a modular architecture with 6 core Python modules each having a single defined responsibility
- Designed a JSON-based baseline storage system with metadata (timestamp, directory, file count) and backward-compatible loading
- Created a Flask web dashboard displaying color-coded security alerts (HIGH/MEDIUM/INFO severity) with Bootstrap 5 UI
- Wrote 33 automated unit tests using Python's unittest module covering all edge cases including corrupted files, empty directories, and inaccessible files
- Implemented application-wide logging using Python's logging module capturing all security events to fim.log

**GitHub line on resume:**  
GitHub: `github.com/YOURUSERNAME/file-integrity-monitor`

---

# PART 9 — QUICK CHEAT SHEET (Read Right Before Interview)

```
PROJECT: File Integrity Monitoring System
PURPOSE: Detect unauthorized file changes using SHA-256 hashes
LANGUAGE: Python 3 (built-ins only + Flask for web UI)
INTERFACE: Browser at http://localhost:5000 (run python app.py)

SHA-256:
  → 64-character hex fingerprint for every file
  → Deterministic (same file = same hash always)
  → Avalanche effect (1 char change = completely different hash)
  → One-way (cannot reverse hash to get file content)

WORKFLOW:
  1. Create Baseline → saves SHA-256 hash of every file to JSON
  2. Scan → recomputes hashes, compares to baseline
  3. MODIFIED = same file, different hash (content changed)
  4. DELETED  = in baseline, not in scan (file removed)
  5. NEW      = not in baseline, in scan (file appeared)
  6. UNCHANGED = same file, same hash (file intact)

SECURITY CONCEPT: CIA Triad → Integrity component
REAL-WORLD USE: SOC environments, PCI-DSS compliance, Tripwire/OSSEC/Wazuh
LIMITATION: On-demand (not real-time), baseline can be tampered

MODULES:
  config.py   → all settings (hash algo, paths, chunk size)
  hasher.py   → hash_file(), hash_folder() with os.walk()
  baseline.py → save_baseline(), load_baseline(), save_alerts(), load_alerts()
  monitor.py  → detect_changes(), has_any_changes(), count_changes()
  reporter.py → display_report() with ANSI colors
  main.py     → CLI menu (5 options)
  app.py      → Flask web interface (4 routes)

TESTS: 33 tests in tests/ folder, run: python -m unittest discover tests/ -v
```

---

*You built this project. You understand every line of it. Go into that interview with confidence.*
