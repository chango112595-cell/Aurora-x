#!/usr/bin/env python3
from pathlib import Path
import sys
from aurora_x.spec.parser_v2 import parse
from aurora_x.synthesis.search import synthesize

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/spec_compile.py <spec.md>"); return
    sp = Path(sys.argv[1]); md = sp.read_text(encoding="utf-8")
    spec = parse(md)
    out = synthesize(spec, Path("runs"))
    print("[OK] Generated:", out)
    print("Source:", out/"src")
    print("Tests:", out/"tests")
    print("Report:", out/"report.html")
    print(f"Run tests: python -m unittest discover -s {out/'tests'} -t {out}")
if __name__ == "__main__":
    main()
