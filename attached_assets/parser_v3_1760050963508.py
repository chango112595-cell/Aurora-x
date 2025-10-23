from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Example:
    inputs: dict[str, Any]
    output: Any


@dataclass
class FunctionSpec:
    name: str
    signature: str
    description: str = ""
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    examples: list[Example] = field(default_factory=list)


@dataclass
class RichSpecV3:
    title: str
    functions: list[FunctionSpec] = field(default_factory=list)


SIG_RE = re.compile(r"def\s+([A-Za-z_]\w*)\s*\((.*?)\)\s*->\s*([A-Za-z_\[\],\s]+)")


def _coerce(val: str):
    val = val.strip()
    if re.fullmatch(r"-?\d+", val):
        return int(val)
    if re.fullmatch(r"-?\d+\.\d+", val):
        return float(val)
    if val.lower() in ("true", "false"):
        return val.lower() == "true"
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    return val


def parse_examples(block: str) -> list[Example]:
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    start = None
    for i, ln in enumerate(lines):
        if ln.startswith("|") and ln.endswith("|") and ("out" in ln or "output" in ln):
            start = i
            break
    if start is None:
        return []
    header = [h.strip(" `") for h in lines[start].strip("|").split("|")]
    out_key = "out" if "out" in header else "output"
    rows = []
    for ln in lines[start + 2 :]:
        if not ln.startswith("|"):
            break
        cells = [c.strip() for c in ln.strip("|").split("|")]
        rows.append(dict(zip(header, cells, strict=False)))
    exs = []
    for r in rows:
        inp = {k: _coerce(v) for k, v in r.items() if k not in (out_key,)}
        exs.append(Example(inputs=inp, output=_coerce(r[out_key])))
    return exs


def parse_functions(md: str) -> list[FunctionSpec]:
    chunks = re.split(r"(?m)^###\s+Function\s+", md)
    out: list[FunctionSpec] = []
    for ch in chunks:
        ch = ch.strip()
        if not ch:
            continue
        lines = ch.splitlines()
        name = lines[0].strip()
        m_sig = re.search(r"```(.*?)```", ch, flags=re.S)
        signature = m_sig.group(1).strip() if m_sig else ""
        desc_m = re.search(r"(?ms)^####\s+Description\s*\n(.*?)(?:(?:^####\s+)|\Z)", ch)
        desc = desc_m.group(1).strip() if desc_m else ""

        def list_block(h: str):
            m = re.search(rf"(?ms)^####\s+{h}\s*\n(.*?)(?:(?:^####\s+)|\Z)", ch)
            if not m:
                return []
            return [ln.strip("- ").strip() for ln in m.group(1).splitlines() if ln.strip()]

        pre = list_block("Preconditions")
        post = list_block("Postconditions")
        ex_m = re.search(r"(?ms)^####\s+Examples\s*\n(.*?)(?:(?:^####\s+)|\Z)", ch)
        exs = parse_examples(ex_m.group(1)) if ex_m else []
        out.append(
            FunctionSpec(
                name=name, signature=signature, description=desc, preconditions=pre, postconditions=post, examples=exs
            )
        )
    return out


def parse_v3(md: str) -> RichSpecV3:
    title = (md.splitlines()[0] if md.startswith("#") else "SpecV3").replace("#", "").strip()
    if "### Function" in md:
        funcs = parse_functions(md)
    else:
        sig = re.search(r"```(.*?)```", md, flags=re.S)
        signature = sig.group(1).strip() if sig else ""
        desc_m = re.search(r"(?ms)^##\s+Description\s*\n(.*?)(?:(?:^##\s+)|\Z)", md)
        desc = desc_m.group(1).strip() if desc_m else ""
        ex_m = re.search(r"(?ms)^##\s+Examples\s*\n(.*?)(?:(?:^##\s+)|\Z)", md)
        post_m = re.search(r"(?ms)^##\s+Postconditions\s*\n(.*?)(?:(?:^##\s+)|\Z)", md)
        exs = parse_examples(ex_m.group(1)) if ex_m else []
        post = [ln.strip("- ").strip() for ln in post_m.group(1).splitlines()] if post_m else []
        funcs = [
            FunctionSpec(
                name=signature.split("(")[0].split()[-1],
                signature=signature,
                description=desc,
                postconditions=post,
                examples=exs,
            )
        ]
    return RichSpecV3(title=title, functions=funcs)
