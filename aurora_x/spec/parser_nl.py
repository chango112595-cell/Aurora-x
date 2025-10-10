from __future__ import annotations
import re, hashlib

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
    if "factorial" in t:
        return NLParseResult({
            "name": "factorial",
            "signature": "def factorial(n: int) -> int",
            "description": "Calculate the factorial of a non-negative integer.",
            "examples": [
                {"n": 0, "out": 1},
                {"n": 5, "out": 120},
                {"n": 3, "out": 6}
            ]
        })
    if "palindrome" in t:
        return NLParseResult({
            "name": "is_palindrome",
            "signature": "def is_palindrome(s: str) -> bool",
            "description": "Check if a string is a palindrome (reads same forwards and backwards).",
            "examples": [
                {"s": "racecar", "out": True},
                {"s": "hello", "out": False},
                {"s": "a", "out": True}
            ]
        })
    if "fibonacci" in t:
        return NLParseResult({
            "name": "fibonacci",
            "signature": "def fibonacci(n: int) -> int",
            "description": "Return the nth number in the Fibonacci sequence.",
            "examples": [
                {"n": 0, "out": 0},
                {"n": 1, "out": 1},
                {"n": 6, "out": 8}
            ]
        })
    if ("prime" in t) and ("check" in t or "is" in t):
        return NLParseResult({
            "name": "is_prime",
            "signature": "def is_prime(n: int) -> bool",
            "description": "Check if a number is prime.",
            "examples": [
                {"n": 2, "out": True},
                {"n": 17, "out": True},
                {"n": 4, "out": False}
            ]
        })
    if ("sort" in t) and ("list" in t or "array" in t):
        return NLParseResult({
            "name": "sort_list",
            "signature": "def sort_list(nums: list[int]) -> list[int]",
            "description": "Sort a list of integers in ascending order.",
            "examples": [
                {"nums": [3,1,2], "out": [1,2,3]},
                {"nums": [5,-1,0], "out": [-1,0,5]}
            ]
        })
    if ("count" in t) and ("vowel" in t):
        return NLParseResult({
            "name": "count_vowels",
            "signature": "def count_vowels(s: str) -> int",
            "description": "Count the number of vowels in a string.",
            "examples": [
                {"s": "hello", "out": 2},
                {"s": "xyz", "out": 0},
                {"s": "aeiou", "out": 5}
            ]
        })
    if ("gcd" in t) or ("greatest common divisor" in t):
        return NLParseResult({
            "name": "gcd",
            "signature": "def gcd(a: int, b: int) -> int",
            "description": "Find the greatest common divisor of two numbers.",
            "examples": [
                {"a": 12, "b": 8, "out": 4},
                {"a": 17, "b": 5, "out": 1}
            ]
        })
    return NLParseResult({
        "name": f"auto_{_hash(t)}",
        "signature": "def todo_spec() -> None",
        "description": "Unrecognized intent; placeholder spec.",
        "examples": []
    })