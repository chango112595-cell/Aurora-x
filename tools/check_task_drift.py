#!/usr/bin/env python3
from __future__ import annotations

import difflib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "MASTER_TASK_LIST.md"
TARGET = ROOT / "aurora_X.md"  # change if your target file differs

BEGIN = "<!-- AURORA_TRACKER_BEGIN -->"
END = "<!-- AURORA_TRACKER_END -->"


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def extract_block(text: str) -> str:
    if BEGIN in text and END in text:
        return text.split(BEGIN, 1)[1].split(END, 1)[0]
    return ""


def normalize(s: str) -> list[str]:
    lines = [ln.rstrip() for ln in s.strip().splitlines() if ln.strip()]
    return lines


def main():
    if not MASTER.exists():
        print("[drift] MASTER_TASK_LIST.md missing; run tools/update_progress.py first.")
        sys.exit(1)
    target = read_text(TARGET)
    if not target:
        print(f"[drift] {TARGET.name} missing; cannot compare.")
        sys.exit(1)

    block = extract_block(target)
    if not block:
        print(
            f"[drift] No tracker block markers in {TARGET.name}. Expected markers:\n{BEGIN}\n...\n{END}"
        )
        sys.exit(1)

    master_norm = normalize(read_text(MASTER))
    block_norm = normalize(block)

    if master_norm != block_norm:
        print("[drift] aurora_X.md tracker section differs from MASTER_TASK_LIST.md")
        diff = difflib.unified_diff(
            block_norm,
            master_norm,
            fromfile="aurora_X.md::tracker",
            tofile="MASTER_TASK_LIST.md",
            lineterm="",
        )
        for line in diff:
            print(line)
        sys.exit(2)

    print("[ok] No drift detected.")
    sys.exit(0)


if __name__ == "__main__":
    main()
