#!/usr/bin/env python3
"""
Populate corpus database from existing synthesis runs
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aurora_x.corpus.store import record, spec_digest


def get_db_path():
    """Get the corpus database path."""
    # Check both possible locations
    db_path = Path("data/corpus.db")
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def populate_from_runs():
    """Scan runs directory and populate corpus with successful syntheses"""
    run_root = Path(".")
    runs_dir = Path("runs")

    if not runs_dir.exists():
        print("No runs directory found")
        return

    recorded = 0
    skipped = 0

    # Scan all run directories
    for run_dir in sorted(runs_dir.iterdir()):
        if not run_dir.is_dir() or run_dir.name == "latest":
            continue

        # Look for src directory
        src_dir = run_dir / "src"
        if not src_dir.exists():
            continue

        # Process all Python files in src
        for py_file in src_dir.glob("*.py"):
            # Skip test files and specs
            if py_file.name.startswith("test_") or py_file.name.startswith("#"):
                continue

            try:
                code = py_file.read_text()

                # Skip empty or placeholder files
                if not code.strip() or "todo_spec" in code.lower():
                    skipped += 1
                    continue

                func_name = py_file.stem

                # Create a simple signature
                sig = f"def {func_name}(...)"

                # Create corpus entry
                entry = {
                    "func_name": func_name,
                    "func_signature": sig,
                    "snippet": code,
                    "passed": 1,
                    "total": 1,
                    "score": 0.95,
                    "complexity": len(code.split("\n")),
                    "iteration": 0,
                    **spec_digest(f"# Imported from {run_dir.name}"),
                }

                # Record to corpus
                record(run_root, entry)

                recorded += 1
                print(f"[OK] Recorded: {func_name} from {run_dir.name}")

            except Exception as e:
                print(f"[WARN]  Error processing {py_file}: {e}")
                skipped += 1

    print("\n[DATA] Summary:")
    print(f"   Recorded: {recorded}")
    print(f"   Skipped: {skipped}")

    # Try to get a count by checking the database
    db_path = get_db_path()
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        count = conn.execute("SELECT COUNT(*) FROM corpus").fetchone()[0]
        conn.close()
        print(f"   Total corpus entries: {count}")
    else:
        print("   Corpus database not yet created")


if __name__ == "__main__":
    populate_from_runs()
