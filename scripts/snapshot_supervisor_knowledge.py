#!/usr/bin/env python3
"""Create tracked snapshots of the Aurora Supervisor knowledge artifacts.

The runtime copies under aurora_supervisor/data/knowledge/ are excluded from Git because they change constantly.
This helper copies those files into a tracked snapshot directory once per 24 hours (or when --force is set).
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_ROOT = ROOT / "aurora_supervisor" / "data" / "knowledge"
EVENTS_SOURCE = KNOWLEDGE_ROOT / "events.jsonl"
STATE_SOURCE = KNOWLEDGE_ROOT / "models" / "state_snapshot.json"
SNAPSHOT_ROOT = KNOWLEDGE_ROOT.parent / "knowledge_snapshots"
LATEST_EVENTS = SNAPSHOT_ROOT / "latest_events.jsonl"
LATEST_STATE = SNAPSHOT_ROOT / "latest_state_snapshot.json"
DAILY_DIR = SNAPSHOT_ROOT / "daily"
MIN_INTERVAL = timedelta(hours=24)


def ensure_snapshot_dir() -> None:
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)


def should_update(dest: Path, force: bool) -> bool:
    if force or not dest.exists():
        return True
    mtime = datetime.fromtimestamp(dest.stat().st_mtime)
    return datetime.now() - mtime >= MIN_INTERVAL


def copy_snapshot(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def write_daily(src: Path, label: str) -> None:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    candidate_dir = DAILY_DIR / timestamp
    candidate_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, candidate_dir / f"{label}.json")


def run(force: bool) -> None:
    if not EVENTS_SOURCE.exists() or not STATE_SOURCE.exists():
        raise FileNotFoundError("Aurora supervisor knowledge files not found; run this script from the repo root after starting Aurora.")

    ensure_snapshot_dir()

    events_updated = should_update(LATEST_EVENTS, force)
    state_updated = should_update(LATEST_STATE, force)

    if events_updated:
        copy_snapshot(EVENTS_SOURCE, LATEST_EVENTS)
        write_daily(EVENTS_SOURCE, "events")
        print(f"Snapshot events -> {LATEST_EVENTS}")
    else:
        print("Events snapshot is up-to-date (last snapshot <24h old).")

    if state_updated:
        copy_snapshot(STATE_SOURCE, LATEST_STATE)
        write_daily(STATE_SOURCE, "state_snapshot")
        print(f"Snapshot state -> {LATEST_STATE}")
    else:
        print("State snapshot is up-to-date (last snapshot <24h old).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh Aurora supervisor knowledge snapshots.")
    parser.add_argument("--force", action="store_true", help="Write a snapshot even if <24h has passed.")
    args = parser.parse_args()
    run(force=args.force)
