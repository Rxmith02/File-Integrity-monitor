"""
app.py — Web Interface for the File Integrity Monitoring System
================================================================
Provides a browser-based UI so you can demo the project visually.

HOW TO RUN:
    pip install flask
    python app.py

Then open your browser at:  http://localhost:5000
"""

import logging
import os
import sys

from flask import Flask, flash, redirect, render_template, request, url_for

# Import the core FIM modules (same ones used by main.py)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baseline import load_alerts, load_baseline, save_alerts, save_baseline
from config   import DATA_DIR, LOGS_DIR
from hasher   import hash_folder
from monitor  import count_changes, detect_changes

# ── Flask app setup ───────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "fim-secure-demo-key-2026"   # required for flash messages

# Silence module-level loggers so the web UI console stays clean
logging.disable(logging.WARNING)


# ── Helper ────────────────────────────────────────────────────────────────────

def _exclude_paths():
    """Return paths that should never be scanned (app's own data and logs)."""
    return {
        os.path.abspath(DATA_DIR),
        os.path.abspath(LOGS_DIR),
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Dashboard — shows baseline status and action forms."""
    hash_dict, metadata = load_baseline()
    baseline_exists = hash_dict is not None
    return render_template("index.html",
                           baseline_exists=baseline_exists,
                           metadata=metadata)


@app.route("/create-baseline", methods=["POST"])
def create_baseline():
    """Step 1 — hash every file in the chosen folder and save baseline.json."""
    folder = request.form.get("folder_path", "").strip().strip('"').strip("'")

    if not folder or not os.path.isdir(folder):
        flash("Folder not found. Please enter a valid folder path.", "danger")
        return redirect(url_for("index"))

    hash_dict = hash_folder(folder, exclude_paths=_exclude_paths())

    if not hash_dict:
        flash("No readable files found in that folder.", "warning")
        return redirect(url_for("index"))

    save_baseline(hash_dict, monitored_directory=folder)
    flash(f"Baseline created successfully!  {len(hash_dict)} file(s) recorded.", "success")
    return redirect(url_for("index"))


@app.route("/scan", methods=["POST"])
def scan():
    """Step 2 — re-hash the folder and compare against the baseline."""
    folder = request.form.get("folder_path", "").strip().strip('"').strip("'")

    if not folder or not os.path.isdir(folder):
        flash("Folder not found. Please enter a valid folder path.", "danger")
        return redirect(url_for("index"))

    baseline_dict, metadata = load_baseline()
    if baseline_dict is None:
        flash("No baseline found. Please create a baseline first (Step 1).", "danger")
        return redirect(url_for("index"))

    current_dict = hash_folder(folder, exclude_paths=_exclude_paths())
    changes      = detect_changes(baseline_dict, current_dict)

    # Build the unchanged list for display
    unchanged = sorted([
        p for p in baseline_dict
        if p in current_dict and current_dict[p] == baseline_dict[p]
    ])

    save_alerts(changes, monitored_directory=folder)

    return render_template("result.html",
                           changes=changes,
                           unchanged=unchanged,
                           folder=folder,
                           counts=count_changes(changes),
                           baseline_meta=metadata)


@app.route("/alerts")
def view_alerts():
    """Step 3 — display the most recently saved scan results."""
    changes, metadata = load_alerts()

    if changes is None:
        flash("No scan results found. Please run a scan first.", "warning")
        return redirect(url_for("index"))

    return render_template("alerts.html",
                           changes=changes,
                           metadata=metadata,
                           counts=count_changes(changes))


@app.route("/update-baseline", methods=["POST"])
def update_baseline():
    """Step 4 — overwrite the baseline with the current file state."""
    folder = request.form.get("folder_path", "").strip().strip('"').strip("'")

    if not folder or not os.path.isdir(folder):
        flash("Folder not found. Please enter a valid folder path.", "danger")
        return redirect(url_for("index"))

    hash_dict = hash_folder(folder, exclude_paths=_exclude_paths())

    if not hash_dict:
        flash("No readable files found in that folder.", "warning")
        return redirect(url_for("index"))

    save_baseline(hash_dict, monitored_directory=folder)
    flash(f"Baseline updated successfully!  {len(hash_dict)} file(s) recorded.", "success")
    return redirect(url_for("index"))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("=" * 55)
    print("  FILE INTEGRITY MONITORING SYSTEM")
    print("  Web Interface  —  v1.0.0")
    print("=" * 55)
    print()
    print("  Open your browser and go to:")
    print("  http://localhost:5000")
    print()
    print("  Press Ctrl+C to stop the server.")
    print("=" * 55)
    print()
    app.run(debug=False, port=5000, host="127.0.0.1")
