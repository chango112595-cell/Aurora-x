from __future__ import annotations

import hashlib
import re


class NLParseResult(dict):
    pass


def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8"), usedforsecurity=False).hexdigest()[:8]


def _snake(text: str) -> str:
    """Convert text to snake_case function name"""
    # Clean and prepare text
    t = text.lower().strip()
    # Remove common filler words
    stopwords = [
        "a",
        "an",
        "the",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "in",
        "on",
        "at",
        "me",
        "you",
        "i",
        "we",
        "my",
        "your",
        "please",
        "can",
        "could",
        "would",
    ]
    words = [w for w in re.sub(r"[^\w\s]", "", t).split() if w not in stopwords]

    # Limit to first 3-4 meaningful words
    if len(words) > 4:
        words = words[:4]
    elif len(words) == 0:
        words = ["custom", "function"]

    # Join with underscores
    name = "_".join(words)

    # Ensure valid Python identifier
    if not name or not name[0].isalpha():
        name = "func_" + name

    # Limit length
    if len(name) > 30:
        name = name[:30].rstrip("_")

    return name


def _extract_routes(text: str) -> list:
    """Extract potential routes from the request text"""
    t = text.lower()
    routes = []

    # Common route patterns
    if "home" in t or "landing" in t or "index" in t:
        routes.append({"path": "/", "name": "home"})
    if "about" in t:
        routes.append({"path": "/about", "name": "about"})
    if "contact" in t:
        routes.append({"path": "/contact", "name": "contact"})
    if "login" in t or "signin" in t:
        routes.append({"path": "/login", "name": "login"})
    if "register" in t or "signup" in t:
        routes.append({"path": "/register", "name": "register"})
    if "dashboard" in t:
        routes.append({"path": "/dashboard", "name": "dashboard"})
    if "api" in t:
        routes.append({"path": "/api", "name": "api"})
    if "admin" in t:
        routes.append({"path": "/admin", "name": "admin"})
    if "profile" in t or "user" in t:
        routes.append({"path": "/profile", "name": "profile"})
    if "settings" in t:
        routes.append({"path": "/settings", "name": "settings"})

    # Default to home route if none detected
    if not routes:
        routes.append({"path": "/", "name": "index"})

    return routes


def parse_english(text: str) -> NLParseResult:
    """Parse English request into structured format."""
    text_lower = text.lower().strip()

    # Check for Flask app requests
    if any(kw in text_lower for kw in ["flask", "web app", "web application", "api server", "rest api"]):
        # Compute snake_case name once
        snake_name = _snake(text.split(".")[0].strip() if "." in text else text[:50].strip())
        return NLParseResult(
            {
                "name": snake_name + "_app",
                "signature": f"def {snake_name}_app() -> Flask",
                "description": f"Flask web application: {text}",
                "framework": "flask",  # Key indicator for synthesis pipeline
                "app_type": "web",
                "includes": {
                    "html": "html" in text_lower,
                    "css": "css" in text_lower,
                    "js": "javascript" in text_lower or "js" in text_lower,
                    "timer": "timer" in text_lower,
                    "ui": "ui" in text_lower or "interface" in text_lower or "dashboard" in text_lower,
                    "api": "api" in text_lower or "endpoint" in text_lower or "rest" in text_lower,
                    "database": "database" in text_lower or "db" in text_lower,
                    "auth": "auth" in text_lower or "login" in text_lower or "user" in text_lower,
                },
                "routes": _extract_routes(text),
                "examples": [],  # Flask apps don't have traditional examples
                "template_type": "flask_web_app",
            }
        )

    if "largest" in text_lower or ("max" in text_lower and "list" in text_lower):
        return NLParseResult(
            {
                "name": "max_in_list",
                "signature": "def max_in_list(nums: list[int]) -> int",
                "description": "Return the largest number in a list of integers.",
                "examples": [{"nums": [1, 2, 3], "out": 3}, {"nums": [-5, 10, 0], "out": 10}],
            }
        )
    if ("reverse" in text_lower and "string" in text_lower) or ("reverse" in text_lower and "text" in text_lower):
        return NLParseResult(
            {
                "name": "reverse_string",
                "signature": "def reverse_string(s: str) -> str",
                "description": "Reverse a unicode string.",
                "examples": [{"s": "abc", "out": "cba"}, {"s": "", "out": ""}],
            }
        )
    if ("sum of squares" in text_lower) or ("square each" in text_lower and "sum" in text_lower):
        return NLParseResult(
            {
                "name": "sum_of_squares",
                "signature": "def sum_of_squares(nums: list[int]) -> int",
                "description": "Compute the sum of squares of numbers in a list.",
                "examples": [{"nums": [1, 2, 3], "out": 14}, {"nums": [0, 4, 5], "out": 41}],
            }
        )
    if ("add" in text_lower or "sum" in text_lower) and ("two" in text_lower or "2" in text_lower):
        return NLParseResult(
            {
                "name": "add_two_numbers",
                "signature": "def add_two_numbers(a: int, b: int) -> int",
                "description": "Return the sum of two integers.",
                "examples": [{"a": 1, "b": 2, "out": 3}, {"a": -5, "b": 5, "out": 0}],
            }
        )
    if "factorial" in text_lower:
        return NLParseResult(
            {
                "name": "factorial",
                "signature": "def factorial(n: int) -> int",
                "description": "Calculate the factorial of a non-negative integer.",
                "examples": [{"n": 0, "out": 1}, {"n": 5, "out": 120}, {"n": 3, "out": 6}],
            }
        )
    if "palindrome" in text_lower:
        return NLParseResult(
            {
                "name": "is_palindrome",
                "signature": "def is_palindrome(s: str) -> bool",
                "description": "Check if a string is a palindrome (reads same forwards and backwards).",
                "examples": [
                    {"s": "racecar", "out": True},
                    {"s": "hello", "out": False},
                    {"s": "a", "out": True},
                ],
            }
        )
    if "fibonacci" in text_lower:
        return NLParseResult(
            {
                "name": "fibonacci",
                "signature": "def fibonacci(n: int) -> int",
                "description": "Return the nth number in the Fibonacci sequence.",
                "examples": [{"n": 0, "out": 0}, {"n": 1, "out": 1}, {"n": 6, "out": 8}],
            }
        )
    if ("prime" in text_lower) and ("check" in text_lower or "is" in text_lower):
        return NLParseResult(
            {
                "name": "is_prime",
                "signature": "def is_prime(n: int) -> bool",
                "description": "Check if a number is prime.",
                "examples": [{"n": 2, "out": True}, {"n": 17, "out": True}, {"n": 4, "out": False}],
            }
        )
    if ("sort" in text_lower) and ("list" in text_lower or "array" in text_lower):
        return NLParseResult(
            {
                "name": "sort_list",
                "signature": "def sort_list(nums: list[int]) -> list[int]",
                "description": "Sort a list of integers in ascending order.",
                "examples": [
                    {"nums": [3, 1, 2], "out": [1, 2, 3]},
                    {"nums": [5, -1, 0], "out": [-1, 0, 5]},
                ],
            }
        )
    if ("count" in text_lower) and ("vowel" in text_lower):
        return NLParseResult(
            {
                "name": "count_vowels",
                "signature": "def count_vowels(s: str) -> int",
                "description": "Count the number of vowels in a string.",
                "examples": [
                    {"s": "hello", "out": 2},
                    {"s": "xyz", "out": 0},
                    {"s": "aeiou", "out": 5},
                ],
            }
        )
    if ("gcd" in text_lower) or ("greatest common divisor" in text_lower):
        return NLParseResult(
            {
                "name": "gcd",
                "signature": "def gcd(a: int, b: int) -> int",
                "description": "Find the greatest common divisor of two numbers.",
                "examples": [{"a": 12, "b": 8, "out": 4}, {"a": 17, "b": 5, "out": 1}],
            }
        )

    # Enhanced fallback for unrecognized patterns
    # Generate a properly named function based on the request
    func_name = _snake(text)

    # Determine appropriate return type based on keywords in request
    return_type = "str"  # Default to string for creative/text requests
    if any(
        word in text_lower
        for word in [
            "calculate",
            "compute",
            "count",
            "number",
            "sum",
            "total",
            "how many",
            "value",
            "result",
        ]
    ):
        return_type = "int"
    elif any(word in text_lower for word in ["check", "is", "verify", "validate", "test", "confirm", "determine"]):
        return_type = "bool"
    elif any(word in text_lower for word in ["list", "array", "collection", "items", "all", "multiple", "several"]):
        return_type = "list[str]"
    elif any(
        word in text_lower
        for word in [
            "generate",
            "create",
            "make",
            "produce",
            "write",
            "compose",
            "haiku",
            "poem",
            "story",
            "text",
        ]
    ):
        return_type = "str"

    # Determine if the function needs parameters based on the request
    # Default to no parameters for creative/generative functions
    needs_input = any(
        word in text_lower
        for word in [
            "given",
            "from",
            "input",
            "parameter",
            "argument",
            "process",
            "convert",
            "transform",
        ]
    )

    # Generate appropriate signature
    if needs_input and return_type == "str":
        signature = f"def {func_name}(input_text: str) -> {return_type}"
    elif needs_input and return_type == "int":
        signature = f"def {func_name}(value: int) -> {return_type}"
    elif needs_input and return_type == "bool":
        signature = f"def {func_name}(item: str) -> {return_type}"
    else:
        signature = f"def {func_name}() -> {return_type}"

    # Sanitize text for description
    safe_text = text.strip()
    # Replace special Unicode characters with ASCII equivalents
    safe_text = safe_text.replace("•", "*").replace("→", "->").replace("–", "-").replace("—", "-")
    safe_text = safe_text.replace("（", "(").replace("）", ")").replace("：", ":")
    # Remove or replace any remaining non-ASCII characters
    safe_text = "".join(c if ord(c) < 128 else " " for c in safe_text)
    # Clean up multiple spaces
    safe_text = " ".join(safe_text.split())

    # Create a meaningful description
    description = f"Function to {safe_text}"
    if "generate" in text_lower or "create" in text_lower or "make" in text_lower:
        description = f"Generate output for: {safe_text}"
    elif "calculate" in text_lower or "compute" in text_lower:
        description = f"Calculate result for: {safe_text}"

    # Generate simple examples based on return type
    examples = []
    if return_type == "str" and "() ->" in signature:
        examples = []  # No examples for parameterless string generators
    elif return_type == "int" and "() ->" in signature:
        examples = []  # No examples for parameterless int functions
    elif return_type == "bool" and "(item: str)" in signature:
        examples = [{"item": "test", "out": True}]

    return NLParseResult(
        {
            "name": func_name,
            "signature": signature,
            "description": description,
            "examples": examples,
        }
    )
