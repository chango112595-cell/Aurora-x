#!/usr/bin/env python3
"""
Tool for an operator to list suggestions and apply them after manual review.
Approvals are signed with HMAC using AURORA_OPERATOR_SIGNING_KEY to provide
tamper-evident audit records. For HSM/GPG, replace the signing implementation.
"""

import hashlib
import hmac
import json
import os
from pathlib import Path

SUGGEST_DIR = Path("automotive/suggestions")
APPLIED_DIR = Path("automotive/applied")
SUGGEST_DIR.mkdir(parents=True, exist_ok=True)
APPLIED_DIR.mkdir(parents=True, exist_ok=True)


def _require_operator_key():
    key = os.getenv("AURORA_OPERATOR_SIGNING_KEY")
    if not key:
        raise RuntimeError("AURORA_OPERATOR_SIGNING_KEY must be set to approve suggestions.")
    return key


def _sign_payload(payload: bytes, key: str) -> str:
    return hmac.new(key.encode("utf-8"), payload, hashlib.sha256).hexdigest()


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
    operator = input("Operator name: ").strip() or "operator"
    key = _require_operator_key()
    content = path.read_text()
    payload = json.dumps(
        {"file": path.name, "operator": operator, "content": content},
        sort_keys=True,
    ).encode("utf-8")
    signature = _sign_payload(payload, key)
    approval = {"operator": operator, "signature": signature}
    out = APPLIED_DIR / path.name
    path.rename(out)
    (APPLIED_DIR / f"{path.stem}.sig.json").write_text(json.dumps(approval, indent=2))
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
