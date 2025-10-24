
#!/usr/bin/env python3
"""
Populate corpus database from existing successful synthesis runs
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aurora_x.corpus.store import get_corpus_store

def populate_from_runs():
    """Scan runs directory and populate corpus with successful syntheses"""
    store = get_corpus_store()
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
                
                # Record to corpus with a good score
                store.record_success(
                    sig=sig,
                    code=code,
                    score=0.95,
                    tags=[func_name, "imported-from-runs", run_dir.name]
                )
                
                recorded += 1
                print(f"✅ Recorded: {func_name} from {run_dir.name}")
                
            except Exception as e:
                print(f"⚠️  Error processing {py_file}: {e}")
                skipped += 1
    
    print(f"\n📊 Summary:")
    print(f"   Recorded: {recorded}")
    print(f"   Skipped: {skipped}")
    print(f"   Total corpus entries: {len(list(store.query_top('', top_k=1000)))}")

if __name__ == "__main__":
    populate_from_runs()
