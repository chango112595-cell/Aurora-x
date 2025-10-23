import sys

sys.path.insert(0, ".")
from test_lib_factorial import factorial

# Test basic factorial
assert factorial(0) == 1
assert factorial(5) == 120
assert factorial(10) == 3628800
print("✓ Factorial function tests pass")
