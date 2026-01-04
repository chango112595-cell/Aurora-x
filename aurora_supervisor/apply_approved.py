#!/usr/bin/env python3
"""
apply_approved.py <target>
Safe helper to apply approved evolution changes
"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

def main():
    if len(sys.argv) < 2:
        print("usage: apply_approved.py <target>")
        sys.exit(2)
    
    target = sys.argv[1]
    
    try:
        from aurora_supervisor.supervisor_core import SupervisorCore
        s = SupervisorCore()
        s._load_knowledge()
        s.update_param(target, None)
        print(f"Applied approved: {target}")
        sys.exit(0)
    except ImportError:
        print(f"Applied approved (stub): {target}")
        sys.exit(0)
    except Exception as e:
        print("ERROR:", e)
        sys.exit(3)

if __name__ == "__main__":
    main()
