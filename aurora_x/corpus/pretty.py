from __future__ import annotations
from typing import Dict, Any, Iterable

def truncate(s: str, n: int = 120) -> str:
    if s is None: return ""
    s = str(s).replace("\n","⏎")
    return s if len(s) <= n else s[:n-1] + "…"

def fmt_rows(rows: Iterable[Dict[str, Any]]) -> str:
    out = []
    for i, r in enumerate(rows, 1):
        line = (
            f"{i:>2}. {r.get('func_name')} | {r.get('sig_key') or r.get('func_signature')} | "
            f"pass {r.get('passed')}/{r.get('total')} | score={r.get('score')} | ts={r.get('timestamp')}\n"
            f"    snippet: {truncate(r.get('snippet'), 160)}"
        )
        out.append(line)
    return "\n".join(out) if out else "(no results)"