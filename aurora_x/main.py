#!/usr/bin/env python3
"""Aurora-X Main Orchestrator with Corpus + Seeding (T02)"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

from .corpus.store import record as corpus_record, retrieve as corpus_retrieve, spec_digest
from .corpus.pretty import fmt_rows

def main():
    ap = argparse.ArgumentParser(description="Aurora-X Ultra - Offline Autonomous Coding Engine")
    ap.add_argument("--spec-file", type=str, help="Path to spec file")
    ap.add_argument("--outdir", type=Path, default=Path("runs"), help="Output directory")
    ap.add_argument("--dump-corpus", type=str, help="Signature to query corpus")
    ap.add_argument("--top", type=int, default=10, help="Number of entries to print")
    args = ap.parse_args()

    # Handle corpus dump CLI
    if args.dump_corpus:
        rows = corpus_retrieve(args.outdir/"run-dump", args.dump_corpus, k=args.top)
        print(fmt_rows(rows))
        return 0
    
    # Main synthesis would go here
    print("Aurora-X Ultra - T02 Checkpoint (Corpus + Seeding)")
    print(f"Output directory: {args.outdir}")
    
    if args.spec_file:
        print(f"Processing spec: {args.spec_file}")
        # Synthesis logic would go here
        # For now, just create a sample corpus entry
        spec_text = Path(args.spec_file).read_text() if Path(args.spec_file).exists() else "# test spec"
        spec_meta = spec_digest(spec_text)
        
        # Example corpus recording
        corpus_record(args.outdir/"run-test", {
            "func_name": "example",
            "func_signature": "example() -> str",
            "passed": 1,
            "total": 1,
            "score": 0.0,
            "snippet": "def example():\n    return 'Aurora-X T02'",
            "complexity": 5,
            "iteration": 0,
            **spec_meta
        })
        print("✅ Corpus entry recorded")
    else:
        print("No spec file provided. Use --spec-file to specify.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())