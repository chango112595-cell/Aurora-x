
from __future__ import annotations
from typing import List

def mutate_candidates(code: str) -> List[str]:
    variants = [code]
    if "return" in code:
        variants.append(code.replace("return", "return "))
    return list(dict.fromkeys(variants))
