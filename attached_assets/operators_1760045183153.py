
from __future__ import annotations


def mutate_candidates(code: str) -> list[str]:
    variants = [code]
    if "return" in code:
        variants.append(code.replace("return", "return "))
    return list(dict.fromkeys(variants))
