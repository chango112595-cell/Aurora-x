#!/usr/bin/env python3
"""
Tool for an operator to list suggestions and apply them after manual review.
This tool simulates the human approval flow: operator signs the suggestion with a passphrase (not real crypto in this stub).
In production: integrate HSM / GPG signing + Luminar Nexus v3 human-approval workflow.
"""

from pathlib import Path

SUGGEST_DIR = Path("automotive/suggestions")
APPLIED_DIR = Path("automotive/applied")
SUGGEST_DIR.mkdir(parents=True, exist_ok=True)
APPLIED_DIR.mkdir(parents=True, exist_ok=True)


def list_suggestions():
    return sorted(SUGGEST_DIR.glob("*.json"))


def apply_suggestion(path: Path):
    print("REVIEW FILE:", path)
    with open(path) as fh:
        print(fh.read())
    confirm = input("Apply suggestion? type 'YES' to confirm: ")
    if confirm != "YES":
        print("aborted")
        return
    # In real: operator signs; here we just move file to applied and log
    out = APPLIED_DIR / path.name
    path.rename(out)
    print("Moved to applied:", out)
    # real execution: call safe executor or hand off to certified toolchain
    return out


def run_cli():
    items = list_suggestions()
    if not items:
        print("No suggestions")
        return
    for i, p in enumerate(items):
        print(i, p.name)
    sel = int(input("select index: "))
    apply_suggestion(items[sel])


if __name__ == "__main__":
    run_cli()
