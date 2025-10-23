from __future__ import annotations

import json as _json
from collections.abc import Iterable
from typing import Any


def truncate(s: str | None, n: int = 120) -> str:
    if s is None:
        return ""
    s = str(s).replace("\n", "⏎")
    return s if len(s) <= n else s[: n - 1] + "…"


def fmt_rows(rows: Iterable[dict[str, Any]]) -> str:
    out = []
    for i, r in enumerate(rows, 1):
        line = (
            f"{i:>2}. {r.get('func_name')} | {r.get('sig_key') or r.get('func_signature')} | "
            f"pass {r.get('passed')}/{r.get('total')} | score={r.get('score')} | ts={r.get('timestamp')}\n"
            f"    snippet: {truncate(r.get('snippet'), 160)}"
        )
        out.append(line)
    return "\n".join(out) if out else "(no results)"


def filter_rows(rows: list[dict[str, Any]], term: str | None) -> list[dict[str, Any]]:
    if not term:
        return rows
    t = term.lower()
    out = []
    for r in rows:
        blob = " ".join(
            str(r.get(k, ""))
            for k in ("func_name", "func_signature", "sig_key", "snippet", "timestamp")
        ).lower()
        if t in blob:
            out.append(r)
    return out


def to_json(rows: list[dict[str, Any]]) -> str:
    return _json.dumps(rows, ensure_ascii=False, indent=2)
