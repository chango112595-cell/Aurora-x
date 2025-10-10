from __future__ import annotations
import argparse, sys, subprocess, os
from pathlib import Path
from aurora_x.config.modes import DEFAULT_MODE
from tools.spec_from_text import create_spec_from_text

def main(argv=None):
    p = argparse.ArgumentParser(prog="aurorax", description="Aurora-X Orchestrator")
    p.add_argument("--spec", help="Path to spec markdown to compile → code")
    p.add_argument("--nl", help="Natural language instruction to generate a spec")
    p.add_argument("--mode", default=DEFAULT_MODE, help="safe | explore (placeholder toggle)")
    args = p.parse_args(argv)

    if args.nl:
        sp = create_spec_from_text(args.nl)
        print(f"[OK] Spec generated from English at: {sp}")
        comp = Path("tools/spec_compile_v3.py")
        if comp.exists():
            subprocess.check_call([sys.executable, "tools/spec_compile_v3.py", str(sp)], env=os.environ.copy())
        else:
            print("No v3 compiler found (tools/spec_compile_v3.py). Add v3 pack first.")
        return

    if args.spec:
        comp = Path("tools/spec_compile_v3.py")
        if comp.exists():
            subprocess.check_call([sys.executable, "tools/spec_compile_v3.py", args.spec], env=os.environ.copy())
        else:
            print("No v3 compiler found (tools/spec_compile_v3.py). Add v3 pack first.")
        return

    p.print_help()

if __name__ == "__main__":
    main()
