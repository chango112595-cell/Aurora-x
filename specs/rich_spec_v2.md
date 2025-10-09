# Spec: add_two_numbers

## Signature
```
def add_two_numbers(a: int, b: int) -> int
```

## Description
Return the sum of two integers. Must work for negative numbers and zero.

## Examples
| a | b | out |
| - | - | --- |
| 1 | 2 | 3 |
| -5 | 5 | 0 |
| 0 | 0 | 0 |

## Postconditions
- Result must equal `a + b`.
- The function must not use any external libraries.
- Time complexity O(1).

## Constraints
- Deterministic with fixed seed.
- No I/O, no network, no filesystem access.