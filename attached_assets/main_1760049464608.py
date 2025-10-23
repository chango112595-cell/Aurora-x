from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aurora_x.spec.parser_v2 import parse
from aurora_x.synthesis.search import synthesize


def run_spec(path: str):
    sp = Path(path)
    if not sp.exists():
        print(f"[ERR] Spec not found: {sp}")
        sys.exit(1)
    md = sp.read_text(encoding="utf-8")
    spec = parse(md)
    out = synthesize(spec, Path("runs"))
    print(f"[OK] Generated: {out}")
    print(f" - Source: {out/'src'}\n - Tests: {out/'tests'}\n - Report: {out/'report.html'}")
    print(f"Run tests: python -m unittest discover -s {out/'tests'} -t {out}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="aurorax", description="Aurora-X Orchestrator")
    p.add_argument("--spec", help="Path to spec markdown to compile → code")
    args = p.parse_args(argv)
    if args.spec:
        run_spec(args.spec)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
