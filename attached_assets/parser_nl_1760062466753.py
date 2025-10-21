from __future__ import annotations

import hashlib


class NLParseResult(dict):
    pass

def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]

def parse_english(text: str) -> NLParseResult:
    t = text.strip().lower()
    if "largest" in t or ("max" in t and "list" in t):
        return NLParseResult({
            "name": "max_in_list",
            "signature": "def max_in_list(nums: list[int]) -> int",
            "description": "Return the largest number in a list of integers.",
            "examples": [
                {"nums": [1,2,3], "out": 3},
                {"nums": [-5,10,0], "out": 10}
            ]
        })
    if ("reverse" in t and "string" in t) or ("reverse" in t and "text" in t):
        return NLParseResult({
            "name": "reverse_string",
            "signature": "def reverse_string(s: str) -> str",
            "description": "Reverse a unicode string.",
            "examples": [
                {"s": "abc", "out": "cba"},
                {"s": "", "out": ""}
            ]
        })
    if ("sum of squares" in t) or ("square each" in t and "sum" in t):
        return NLParseResult({
            "name": "sum_of_squares",
            "signature": "def sum_of_squares(nums: list[int]) -> int",
            "description": "Compute the sum of squares of numbers in a list.",
            "examples": [
                {"nums": [1,2,3], "out": 14},
                {"nums": [0,4,5], "out": 41}
            ]
        })
    if ("add" in t or "sum" in t) and ("two" in t or "2" in t):
        return NLParseResult({
            "name": "add_two_numbers",
            "signature": "def add_two_numbers(a: int, b: int) -> int",
            "description": "Return the sum of two integers.",
            "examples": [
                {"a": 1, "b": 2, "out": 3},
                {"a": -5, "b": 5, "out": 0}
            ]
        })
    return NLParseResult({
        "name": f"auto_{_hash(t)}",
        "signature": "def todo_spec() -> None",
        "description": "Unrecognized intent; placeholder spec.",
        "examples": []
    })
