#!/usr/bin/env python3
"""Aurora-X main module with corpus integration."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from .corpus.store import record as corpus_record, retrieve as corpus_retrieve, spec_digest
from .corpus.pretty import fmt_rows

def main():
    """Main entry point for Aurora-X."""
    ap = argparse.ArgumentParser(description="Aurora-X Autonomous Code Synthesis Engine")
    ap.add_argument("--spec", type=str, help="Path to spec file")
    ap.add_argument("--outdir", type=Path, default=Path("runs"), help="Output directory")
    ap.add_argument("--dump-corpus", type=str, help="Signature to query corpus")
    ap.add_argument("--top", type=int, default=10, help="Number of entries to print")
    ap.add_argument("--max-iter", type=int, default=100, help="Maximum synthesis iterations")
    ap.add_argument("--seed-bias", type=float, default=0.0, help="Seed bias [0.0-0.5]")
    ap.add_argument("--beam", type=int, default=5, help="Beam search width")
    args = ap.parse_args()
    
    # Handle corpus dump query
    if args.dump_corpus:
        rows = corpus_retrieve(args.outdir/"run-dump", args.dump_corpus, k=args.top)
        print(fmt_rows(rows))
        return 0
    
    # Main synthesis flow (stub for now)
    if not args.spec:
        print("No spec file provided. Use --spec or --dump-corpus.")
        return 1
    
    print(f"Aurora-X synthesis started with:")
    print(f"  Spec: {args.spec}")
    print(f"  Seed bias: {args.seed_bias}")
    print(f"  Beam width: {args.beam}")
    print(f"  Max iterations: {args.max_iter}")
    
    # Example corpus recording (would be done after actual synthesis)
    # corpus_record(args.outdir, {
    #     "func_name": "example_func",
    #     "func_signature": "example_func(x:int)->int",
    #     "passed": 5,
    #     "total": 5,
    #     "score": 1.0,
    #     "snippet": "def example_func(x): return x * 2",
    #     "complexity": 1,
    #     **spec_digest("# Example spec")
    # })
    
    return 0

if __name__ == "__main__":
    sys.exit(main())