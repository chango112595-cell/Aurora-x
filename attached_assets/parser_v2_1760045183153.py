
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Example:
    inputs: dict[str, Any]
    output: Any

@dataclass
class RichSpec:
    title: str
    signature: str
    description: str
    examples: list[Example] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

SIG_RE = re.compile(r"def\s+([a-zA-Z_]\w*)\s*\((.*?)\)\s*->\s*([a-zA-Z_][\w\[\], ]*)")

def parse_signature(block: str):
    m = SIG_RE.search(block)
    if not m:
        raise ValueError("Invalid signature block")
    name = m.group(1)
    args = [p.strip() for p in m.group(2).split(",") if p.strip()]
    rtype = m.group(3).strip()
    return name, args, rtype

def parse_examples(md: str) -> list[Example]:
    lines = [ln.strip() for ln in md.splitlines() if ln.strip()]
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("|") and ln.endswith("|") and "out" in ln.lower():
            start = i; break
    if start is None:
        return []
    header = [h.strip().strip("`") for h in lines[start].strip("|").split("|")]
    rows = []
    for ln in lines[start+2:]:
        if not ln.startswith("|"): break
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows.append(dict(zip(header, cells, strict=False)))
    examples = []
    for row in rows:
        inp = {k: _coerce(row[k]) for k in row if k.lower() not in ("out", "output")}
        out_key = "out" if "out" in row else "output"
        examples.append(Example(inputs=inp, output=_coerce(row[out_key])))
    return examples

def _coerce(s: str):
    if re.fullmatch(r"-?\d+", s): return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s): return float(s)
    if s.lower() in ("true","false"): return s.lower()=="true"
    return s

def parse_sections(md: str):
    out = {}
    current = None
    buf = []
    def flush():
        nonlocal current, buf
        if current: out[current] = "\n".join(buf).strip()
    for ln in md.splitlines():
        if ln.startswith("## "):
            flush()
            current = ln[3:].strip()
            buf = []
        else:
            buf.append(ln)
    flush()
    return out

def parse(md: str) -> RichSpec:
    (md.splitlines()[0] or "# Spec").replace("#","").strip()
    sections = parse_sections(md)
    import re as _re
    sig_block = sections.get("Signature","")
    sig_code = _re.search(r"```(.*?)```", sig_block, flags=_re.S|_re.M)
    if not sig_code:
        raise ValueError("Signature must be in a code block")
    signature = sig_code.group(1).strip()
    name, args, rtype = parse_signature(signature)
    examples = parse_examples(sections.get("Examples",""))
    post = [ln.strip("- ").strip() for ln in sections.get("Postconditions","").splitlines() if ln.strip()]
    cons = [ln.strip("- ").strip() for ln in sections.get("Constraints","").splitlines() if ln.strip()]
    return RichSpec(title=name, signature=signature, description=sections.get("Description","").strip(),
                    examples=examples, postconditions=post, constraints=cons)
