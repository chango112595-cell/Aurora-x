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

def _snake(name: str) -> str:
    """Convert text to snake_case."""
    # Remove special characters and convert to lowercase
    name = re.sub(r'[^\w\s]', '', name)
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Convert to lowercase
    name = name.lower()
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    return name if name else 'function'

def english_to_spec(utterance: str) -> str:
    """Convert English utterance to a spec markdown."""
    # Import parser_nl to get proper parsing including Flask detection
    from aurora_x.spec.parser_nl import parse_english

    # Parse the utterance using parser_nl
    parsed = parse_english(utterance)

    # Check if this is a Flask request
    if parsed.get("framework") == "flask":
        # Generate Flask-specific spec
        return f"""# {parsed['name']}

## Metadata
- Framework: Flask
- Type: Web Application
- Generated: Auto

## Signature
```
{parsed['signature']}
```

## Description
{parsed['description']}

## Flask Configuration
- Routes: {parsed.get('routes', [])}
- Includes: {parsed.get('includes', {})}

## Examples
Flask applications do not have traditional input/output examples.
This will generate a complete Flask web application.
"""

    # Fall back to existing pattern matching for non-Flask requests
    lower_utterance = utterance.lower()

    # Check if parser_nl found a known pattern
    if parsed.get("signature") and parsed.get("name") != _snake(utterance):
        # Use parser_nl's result for known patterns
        examples_md = ""
        if parsed.get("examples"):
            examples_md = "| " + " | ".join(list(parsed["examples"][0].keys()) + ["out"]) + " |\n"
            examples_md += "|" + "---|" * (len(parsed["examples"][0]) + 1) + "\n"
            for ex in parsed["examples"]:
                row = " | ".join([str(ex.get(k, "")) for k in list(ex.keys())[:-1]] + [str(ex.get("out", ""))])
                examples_md += f"| {row} |\n"

        return f"""# {parsed['name']}

## Signature
```
{parsed['signature']}
```

## Description
{parsed['description']}

## Examples
{examples_md if examples_md else "No examples provided"}

## Postconditions
- Generated from natural language
"""

    # Recognize common patterns (fallback for backward compatibility)
    if "reverse" in lower_utterance and "string" in lower_utterance:
        return """# reverse_string

## Signature
```
def reverse_string(s: str) -> str
```

## Description
Reverse the input string.

## Examples
| s | out |
|---|-----|
| hello | olleh |
| world | dlrow |
| python | nohtyp |

## Postconditions
- The output is the input string in reverse order
"""
    elif ("add" in lower_utterance or "sum" in lower_utterance) and ("two" in lower_utterance or "numbers" in lower_utterance):
        return """# add_two_numbers

## Signature
```
def add_two_numbers(a: int, b: int) -> int
```

## Description
Add two numbers together.

## Examples
| a | b | out |
|---|---|-----|
| 2 | 3 | 5 |
| 10 | 20 | 30 |
| -5 | 5 | 0 |

## Postconditions
- The output is the sum of the two input numbers
"""
    elif "factorial" in lower_utterance:
        return """# factorial

## Signature
```
def factorial(n: int) -> int
```

## Description
Calculate the factorial of a non-negative integer.

## Examples
| n | out |
|---|-----|
| 0 | 1 |
| 5 | 120 |
| 3 | 6 |

## Postconditions
- Returns n! (n factorial)
- Returns 1 for n=0
"""
    elif "palindrome" in lower_utterance:
        return """# is_palindrome

## Signature
```
def is_palindrome(s: str) -> bool
```

## Description
Check if a string is a palindrome.

## Examples
| s | out |
|---|-----|
| racecar | true |
| hello | false |
| noon | true |

## Postconditions
- Returns true if the string reads the same forwards and backwards
"""
    elif "fibonacci" in lower_utterance or "fib" in lower_utterance:
        return """# fibonacci

## Signature
```
def fibonacci(n: int) -> int
```

## Description
Return the nth Fibonacci number.

## Examples
| n | out |
|---|-----|
| 0 | 0 |
| 1 | 1 |
| 5 | 5 |

## Postconditions
- Returns the nth number in the Fibonacci sequence
"""
    elif "prime" in lower_utterance:
        return """# is_prime

## Signature
```
def is_prime(n: int) -> bool
```

## Description
Check if a number is prime.

## Examples
| n | out |
|---|-----|
| 2 | true |
| 4 | false |
| 17 | true |

## Postconditions
- Returns true if n is a prime number
"""
    elif "timer" in lower_utterance or "countdown" in lower_utterance:
        return """# timer_function

## Signature
```
def timer_function(seconds: int) -> str
```

## Description
Create a timer or countdown function.

## Examples
| seconds | out |
|---|-----|
| 60 | 1:00 |
| 90 | 1:30 |
| 120 | 2:00 |

## Postconditions
- Returns formatted time string
"""
    else:
        # Generic fallback for unrecognized patterns
        func_name = _snake(utterance)
        if not func_name or func_name == 'function':
            func_name = "generated_function"

        return f"""# {func_name}

## Signature
```
def {func_name}(input_value: str) -> str
```

## Description
{utterance}

## Examples
| input_value | out |
|---|-----|
| test | test_result |
| example | example_result |

## Postconditions
- Implements the requested functionality: {utterance}
"""

def parse_freeform_or_v2(text: str) -> RichSpec:
    """Try to parse as v2 spec first, fall back to English if that fails."""
    # First check if it looks like a markdown spec
    if "## Signature" in text or "```" in text:
        try:
            # Try v2 parser
            return parse(text)
        except Exception as e:
            print(f"[Parser] V2 parse failed: {e}, falling back to English mode")

    # Fall back to English-to-spec conversion
    spec_md = english_to_spec(text)
    try:
        return parse(spec_md)
    except Exception as e:
        print(f"[Parser] English-to-spec parse failed: {e}, using minimal spec")
        # Last resort: create a minimal spec
        func_name = _snake(text) or "function"
        return RichSpec(
            title=func_name,
            signature=f"def {func_name}(input_value: str) -> str",
            description=text,
            examples=[Example(inputs={"input_value": "test"}, output="test_result")],
            postconditions=[f"Implements: {text}"],
            constraints=[]
        )
