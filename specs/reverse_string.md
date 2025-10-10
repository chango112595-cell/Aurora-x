# Spec: reverse_string

## Signature
```
def reverse_string(s: str) -> str
```

## Description
Reverse the input string. The function must handle empty strings and unicode.

## Examples
| s | out |
| - | --- |
| "abc" | "cba" |
| "" | "" |
| "åß∂" | "∂ßå" |

## Postconditions
- Result equals input reversed using slicing.
- No external libraries.

## Constraints
- Deterministic.
- O(n) time, O(1) extra space (not counting output).# Test spec modification at Fri Oct 10 01:44:49 AM UTC 2025
