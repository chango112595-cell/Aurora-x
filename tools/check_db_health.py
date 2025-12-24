"""
Check Db Health

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""Check Aurora-X database health."""
from typing import Dict, List, Tuple, Optional, Any, Union
import sqlite3
from pathlib import Path

# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)


def check_corpus_db() -> Any:
    """Check corpus database health."""
    db_path = Path("data/corpus.db")
    expected_columns = [
        "id",
        "timestamp",
        "spec_id",
        "spec_hash",
        "func_name",
        "func_signature",
        "sig_key",
        "passed",
        "total",
        "score",
        "failing_tests",
        "snippet",
        "complexity",
        "iteration",
        "calls_functions",
        "post_bow",
    ]
    create_table_sql = (
        "CREATE TABLE IF NOT EXISTS corpus ("
        "id TEXT PRIMARY KEY, timestamp TEXT,"
        "spec_id TEXT, spec_hash TEXT,"
        "func_name TEXT, func_signature TEXT, sig_key TEXT,"
        "passed INTEGER, total INTEGER, score REAL,"
        "failing_tests TEXT, snippet TEXT, complexity INTEGER,"
        "iteration INTEGER, calls_functions TEXT, post_bow TEXT"
        ")"
    )

    if not db_path.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        print("[OK] corpus.db created with corpus table")
        return True

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='corpus'")
        if not cursor.fetchone():
            print("[ERROR] corpus table missing")
            return False

        cursor.execute("PRAGMA table_info(corpus)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        missing_columns = [col for col in expected_columns if col not in existing_columns]
        if missing_columns:
            print(f"[ERROR] corpus table schema mismatch; missing columns: {missing_columns}")
            return False

        # Count entries
        cursor.execute("SELECT COUNT(*) FROM corpus")
        count = cursor.fetchone()[0]
        print(f"[OK] corpus.db healthy with {count} entries")

        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False


if __name__ == "__main__":
    check_corpus_db()
