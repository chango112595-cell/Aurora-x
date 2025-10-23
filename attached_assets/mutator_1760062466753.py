from __future__ import annotations


def mutate_safe(code: str) -> list[str]:
    out = [code]
    if "return" in code:
        out.append(code.replace("return", "return "))
    return list(dict.fromkeys(out))


def mutate_explore(code: str) -> list[str]:
    out = mutate_safe(code)
    if " + " in code:
        out.append(code.replace(" + ", " - "))
    if " - " in code:
        out.append(code.replace(" - ", " + "))
    return list(dict.fromkeys(out))
