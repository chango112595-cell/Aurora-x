#!/usr/bin/env python3
"""
aurora_auto_fix.py

Best-effort automated fixer for the Aurora-X repo.
What it does (attempts):
  - Scans for TODO/FIXME/XXX/HACK markers and records them to fixes_report.json
  - Replaces common placeholder implementations:
        - "return None  # aurora-placeholder" -> "return None  # placeholder"
        - "return None  # aurora-placeholder" -> "return None  # placeholder"
  - For TypeScript/TSX files:
        - Replace occurrences of '/api/conversation' with '/api/chat'
        - Try to ensure fetch responses are parsed with response.json() when missing (best-effort)
        - Record files where manual attention is required
  - For Python files: run `python -m py_compile` on top files found (best-effort)
  - Create backups of any file it modifies (filename + .aurora_backup)
  - Produce a JSON report at ./aurora_auto_fix_report.json summarizing changes and items needing manual work
Limitations & Warnings:
  - This script makes automated, textual fixes. It cannot fully understand runtime logic.
  - Please review changes before committing. The script creates backups for every modified file.
  - Use in a git repo where you can revert if necessary.
Usage:
  cd /path/to/aurora-repo-root
  python3 /path/to/aurora_auto_fix.py --dry-run    # see what it *would* change
  python3 /path/to/aurora_auto_fix.py              # apply changes in-place

"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

MARKERS = ["TODO", "FIXME", "XXX", "HACK", "BUG"]


def find_files(root: Path):
    exts = [".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md"]
    files = []
    for p in root.rglob("*"):
        if p.is_file() and any(p.name.endswith(ext) for ext in exts):
            # skip node_modules, .git, .venv
            if any(part in ("node_modules", ".git", ".venv", "venv") for part in p.parts):
                continue
            files.append(p)
    return files


def backup_file(p: Path):
    bak = p.with_suffix(p.suffix + ".aurora_backup")
    if not bak.exists():
        shutil.copy2(p, bak)
    return bak


def replace_in_file(p: Path, old: str, new: str):
    text = p.read_text(encoding="utf-8", errors="ignore")
    if old not in text:
        return False
    backup_file(p)
    new_text = text.replace(old, new)
    p.write_text(new_text, encoding="utf-8")
    return True


def scan_and_fix(root: Path, dry_run: bool = False):
    files = find_files(root)
    report = {"modified": [], "backups": [], "incomplete_items": [], "errors": []}

    for p in files:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            report["errors"].append({"file": str(p), "error": str(e)})
            continue

        # Record marker lines
        for i, line in enumerate(txt.splitlines(), start=1):
            for m in MARKERS:
                if m in line:
                    report["incomplete_items"].append(
                        {
                            "file": str(p.relative_to(root)),
                            "line": i,
                            "marker": m,
                            "content": line.strip(),
                        }
                    )

        modified = False

        # Python: replace return None  # aurora-placeholder / pass TODO
        if p.suffix == ".py":
            if (
                "return None  # aurora-placeholder" in txt
                or "return None  # aurora-placeholder" in txt
                or re.search(r"pass\s*$", txt, flags=re.M)
            ):
                if not dry_run:
                    backup_file(p)
                    new_txt = re.sub(
                        r"raise\s+NotImplementedError", "return None  # aurora-placeholder", txt
                    )
                    new_txt = new_txt.replace(
                        "return None  # aurora-placeholder", "return None  # aurora-placeholder"
                    )
                    # Replace bare 'pass' inside functions only (best-effort): replace lines that are only '    pass' with '    return None  # aurora-placeholder'
                    new_txt = re.sub(
                        r"(?m)^(\\s+)pass\\s*$", r"\\1return None  # aurora-placeholder", new_txt
                    )
                    p.write_text(new_txt, encoding="utf-8")
                    modified = True

        # TypeScript/TSX fixes: endpoint and fetch handling
        if p.suffix in (".ts", ".tsx", ".js", ".jsx"):
            content = txt
            changes = []
            # Fix wrong endpoint '/api/conversation' -> '/api/chat'
            if "/api/conversation" in content:
                changes.append(("replace_endpoint", "/api/conversation", "/api/chat"))
                if not dry_run:
                    backup_file(p)
                    content = content.replace("/api/conversation", "/api/chat")
                    modified = True

            # Ensure fetch responses use .json() when they access .ok or .runs etc.
            # Best-effort: find patterns like 'fetch(...).then(res => ...' without .json usage
            fetch_patterns = re.findall(r"fetch\\([^)]*\\)(?:\\s*\\.then\\s*\\([^)]*\\))?", content)
            if fetch_patterns:
                # Heuristic: if 'response.json' not in file, try to replace simple 'const data = await response.text()' to json usage
                if "response.json()" not in content and re.search(r"await\\s+fetch\\(", content):
                    # replace 'const data = await response.text()' -> 'const data = await response.json()' (best-effort)
                    if "await response.text()" in content or "response.text()" in content:
                        changes.append(("force_json_text", "response.text()", "response.json()"))
                        if not dry_run:
                            backup_file(p)
                            content = content.replace("response.text()", "response.json()")
                            content = content.replace(
                                "await response.text()", "await response.json()"
                            )
                            modified = True
                # If fetch used with .then and no json, try to add .then(res => res.json()).then(data => ...)
                if ".then(" in content and ".json()" not in content:
                    # This is risky; we just flag for manual review
                    report["incomplete_items"].append(
                        {
                            "file": str(p.relative_to(root)),
                            "line": 1,
                            "marker": "MANUAL_REVIEW",
                            "content": "fetch without .json() usage; please inspect",
                        }
                    )

            if modified and not dry_run:
                p.write_text(content, encoding="utf-8")

        # Simple textual fixes across file types
        if "return None  # aurora-placeholder" in txt or "return None  # aurora-placeholder" in txt:
            # already handled for python; for other files just note
            report["incomplete_items"].append(
                {
                    "file": str(p.relative_to(root)),
                    "line": 1,
                    "marker": "NOT_IMPLEMENTED",
                    "content": "Placeholder implementation found",
                }
            )

        if modified:
            report["modified"].append(str(p.relative_to(root)))
            report["backups"].append(
                str(p.with_suffix(p.suffix + ".aurora_backup").relative_to(root))
            )

    # Run a light Python compile check on top-level python files (best-effort)
    py_files = [f for f in files if f.suffix == ".py"]
    errors = []
    for pf in py_files[:50]:  # limit to first 50 to avoid long runs
        try:
            subprocess.run(
                [sys.executable, "-m", "py_compile", str(pf)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            errors.append({"file": str(pf.relative_to(root)), "error": e.stderr.splitlines()[:5]})

    report["python_compile_errors_sample"] = errors

    # Save report
    report_path = root / "aurora_auto_fix_report.json"
    if not dry_run:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2))

    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root", "-r", default=".", help="Aurora repo root (default: current directory)"
    )
    ap.add_argument("--dry-run", action="store_true", help="Don't write changes; just show report")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    print("Aurora Auto Fix - Running on:", root)
    report = scan_and_fix(root, dry_run=args.dry_run)
    print("Report saved to:", root / "aurora_auto_fix_report.json")
    print("Please review backups (files with .aurora_backup) before committing.")


if __name__ == "__main__":
    main()
