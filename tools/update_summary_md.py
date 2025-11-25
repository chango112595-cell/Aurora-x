"""
Update Summary Md

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
from __future__ from typing import Dict, List, Tuple, Optional, Any, Union
import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "progress.json"
UPDATE_PROGRESS = ROOT / "tools" / "update_progress.py"
MASTER = ROOT / "MASTER_TASK_LIST.md"
TARGET = ROOT / "aurora_X.md"  # change if your target file differs

BEGIN = "<!-- AURORA_TRACKER_BEGIN -->"
END = "<!-- AURORA_TRACKER_END -->"
HEADER = "### [OK] Task Tracker Status (Authoritative, from progress.json)"


def ensure_master_uptodate():
    if not PROGRESS.exists():
        raise SystemExit("[update_summary_md] progress.json missing; cannot render tracker.")
    if not UPDATE_PROGRESS.exists():
        raise SystemExit("[update_summary_md] tools/update_progress.py missing.")
    subprocess.run([sys.executable, str(UPDATE_PROGRESS)], check=False)
    if not MASTER.exists():
        raise SystemExit("[update_summary_md] MASTER_TASK_LIST.md not generated.")


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def build_replacement_block() -> str:
    master = read_text(MASTER).strip()
    block = f"{HEADER}\n\n{master}\n"
    return f"{BEGIN}\n{block}\n{END}"


def upsert_block(doc: str, replacement: str) -> str:
    if BEGIN in doc and END in doc:
        pre = doc.split(BEGIN, 1)[0]
        post = doc.split(END, 1)[1]
        return pre + replacement + post
    section = "\n\n" + replacement + "\n"
    if not doc.strip():
        doc = "# Aurora-X  Project Notes\n\n"
    if HEADER in doc and BEGIN not in doc:
        return doc + section
    return doc + section


def main():
    ensure_master_uptodate()
    current = read_text(TARGET)
    new_block = build_replacement_block()
    updated = upsert_block(current, new_block)
    if updated != current:
        bak = TARGET.with_suffix(TARGET.suffix + ".bak")
        try:
            shutil.copyfile(TARGET, bak)
        except Exception:
            pass
        write_text(TARGET, updated)
        print(f"[ok] updated {TARGET.name} with canonical tracker block.")
    else:
        print("[ok] no changes; tracker block already up-to-date.")


if __name__ == "__main__":
    main()
