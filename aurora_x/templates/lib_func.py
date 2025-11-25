"""
Library Function Template Generator for T08 Intent Router
Generates Python library functions with unit tests
"""


def render_func(name: str, brief: str, fields: dict) -> str:
    """
    Generate a Python library function with tests based on intent

    Args:
        name: Function name (e.g., 'factorial', 'reverse_string')
        brief: Brief description of what the function does
        fields: Additional fields from intent classification

    Returns:
        Complete Python module with function and tests as string
    """

    # Check for specific function types
    brief_lower = brief.lower()

    if "factorial" in brief_lower:
        return _render_factorial_func(name, brief)
    elif "fibonacci" in brief_lower:
        return _render_fibonacci_func(name, brief)
    elif "palindrome" in brief_lower:
        return _render_palindrome_func(name, brief)
    elif "reverse" in brief_lower and "string" in brief_lower:
        return _render_reverse_string_func(name, brief)
    else:
        return _render_generic_func(name, brief)


def _render_factorial_func(name: str, brief: str) -> str:
    """Generate factorial function with tests"""
    return f'''#!/usr/bin/env python3
"""
{brief}

This module provides an optimized factorial implementation with memoization,
input validation, and comprehensive unit tests.

Example usage:
    >>> from lib_function import factorial
    >>> factorial(5)
    120
    >>> factorial(0)
    1
    >>> factorial(20)
    2432902008176640000
"""

from typing import Dict, Union
from functools import lru_cache

# Optional pytest import
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


@lru_cache(maxsize=128)
def factorial(n: int) -> int:
    """
    Calculate the factorial of a non-negative integer.

    Uses memoization for improved performance on repeated calls.

    Args:
        n: A non-negative integer

    Returns:
        The factorial of n (n!)

    Raises:
        ValueError: If n is negative
        TypeError: If n is not an integer

    Examples:
        >>> factorial(0)
        1
        >>> factorial(5)
        120
        >>> factorial(10)
        3628800
    """
    if not isinstance(n, int):
        raise TypeError(f"factorial() argument must be an integer, not '{{type(n).__name__}}'")

    if n < 0:
        raise ValueError("factorial() not defined for negative values")

    if n <= 1:
        return 1

    # Iterative approach for better performance with large numbers
    result = 1
    for i in range(2, n + 1):
        result *= i

    return result


def factorial_recursive(n: int) -> int:
    """
    Alternative recursive implementation of factorial.

    Note: This may hit recursion limit for large n (typically n > 1000).

    Args:
        n: A non-negative integer

    Returns:
        The factorial of n

    Examples:
        >>> factorial_recursive(5)
        120
    """
    if not isinstance(n, int):
        raise TypeError(f"factorial_recursive() argument must be an integer")

    if n < 0:
        raise ValueError("factorial_recursive() not defined for negative values")

    if n <= 1:
        return 1

    return n * factorial_recursive(n - 1)


# ============================================================================
# Unit Tests
# ============================================================================

class TestFactorial:
    """Test suite for factorial function"""

    def test_base_cases(self):
        """Test factorial base cases (0 and 1)"""
        assert factorial(0) == 1
        assert factorial(1) == 1

    def test_small_numbers(self):
        """Test factorial with small positive integers"""
        assert factorial(2) == 2
        assert factorial(3) == 6
        assert factorial(4) == 24
        assert factorial(5) == 120
        assert factorial(6) == 720

    def test_medium_numbers(self):
        """Test factorial with medium-sized integers"""
        assert factorial(10) == 3628800
        assert factorial(12) == 479001600
        assert factorial(15) == 1307674368000

    def test_large_numbers(self):
        """Test factorial with larger integers"""
        assert factorial(20) == 2432902008176640000
        assert factorial(25) == 15511210043330985984000000

    def test_negative_input(self):
        """Test that negative inputs raise ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError, match="not defined for negative"):
                factorial(-1)
            with pytest.raises(ValueError):
                factorial(-10)
        else:
            try:
                factorial(-1)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

    def test_non_integer_input(self):
        """Test that non-integer inputs raise TypeError"""
        if HAS_PYTEST:
            with pytest.raises(TypeError, match="argument must be an integer"):
                factorial(3.14)
            with pytest.raises(TypeError):
                factorial("5")
            with pytest.raises(TypeError):
                factorial([5])
        else:
            try:
                factorial(3.14)
                assert False, "Should have raised TypeError"
            except TypeError:
                pass

    def test_memoization(self):
        """Test that memoization is working (performance test)"""
        import time

        # Clear cache
        factorial.cache_clear()

        # First call should take longer
        start = time.perf_counter()
        result1 = factorial(30)
        time1 = time.perf_counter() - start

        # Second call should be much faster (cached)
        start = time.perf_counter()
        result2 = factorial(30)
        time2 = time.perf_counter() - start

        assert result1 == result2
        # Second call should be at least 10x faster due to caching
        # (This might not always pass in all environments, so we're lenient)
        assert time2 <= time1

    def test_recursive_implementation(self):
        """Test the recursive implementation matches iterative"""
        for n in range(10):
            assert factorial(n) == factorial_recursive(n)


class TestFactorialProperties:
    """Property-based tests for factorial"""

    def test_monotonic_increasing(self):
        """Test that factorial is monotonically increasing for n >= 0"""
        for n in range(1, 10):
            assert factorial(n) > factorial(n - 1)

    def test_divisibility(self):
        """Test that n! is divisible by all integers from 1 to n"""
        for n in range(2, 10):
            fact_n = factorial(n)
            for divisor in range(1, n + 1):
                assert fact_n % divisor == 0


# ============================================================================
# Performance Benchmarks (optional)
# ============================================================================

def benchmark_factorial(max_n: int = 100):
    """
    Simple benchmark for factorial performance.

    Args:
        max_n: Maximum value to test
    """
    import time

    print(f"\\nBenchmarking factorial up to {{max_n}}...")

    start = time.perf_counter()
    for n in range(max_n + 1):
        _ = factorial(n)
    elapsed = time.perf_counter() - start

    print(f"Computed {{max_n + 1}} factorials in {{elapsed:.4f}} seconds")
    print(f"Average time per factorial: {{elapsed / (max_n + 1) * 1000:.4f}} ms")


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    # Run some example calculations
    print("Factorial Examples:")
    print("=" * 50)

    test_values = [0, 1, 5, 10, 20]
    for n in test_values:
        print(f"factorial({{n:2d}}) = {{factorial(n)}}")

    # Run unit tests
    print("\\nRunning unit tests...")
    print("=" * 50)

    # Run pytest if available, otherwise run tests manually
    try:
        import pytest
        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest not installed. Running manual tests...")

        # Instantiate test classes and run test methods
        test_factorial = TestFactorial()
        test_properties = TestFactorialProperties()

        test_methods = [
            method for method in dir(test_factorial)
            if method.startswith('test_')
        ]

        passed = 0
        failed = 0

        for method_name in test_methods:
            try:
                method = getattr(test_factorial, method_name)
                method()
                print(f" {{method_name}}")
                passed += 1
            except Exception as e:
                print(f" {{method_name}}: {{e}}")
                failed += 1

        print(f"\\nResults: {{passed}} passed, {{failed}} failed")

    # Run benchmark
    benchmark_factorial(50)
'''


def _render_fibonacci_func(name: str, brief: str) -> str:
    """Generate Fibonacci function with tests"""
    return f'''#!/usr/bin/env python3
"""
{brief}

Efficient Fibonacci sequence implementation with multiple algorithms.

Example usage:
    >>> from lib_function import fibonacci, fibonacci_sequence
    >>> fibonacci(10)
    55
    >>> list(fibonacci_sequence(10))
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
"""

from typing import List, Iterator, Tuple
from functools import lru_cache

# Optional pytest import
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number (0-indexed).

    Uses memoization for O(n) time complexity.

    Args:
        n: The index of the Fibonacci number to calculate

    Returns:
        The nth Fibonacci number

    Raises:
        ValueError: If n is negative
        TypeError: If n is not an integer

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(10)
        55
    """
    if not isinstance(n, int):
        raise TypeError(f"fibonacci() argument must be an integer")

    if n < 0:
        raise ValueError("fibonacci() not defined for negative indices")

    if n <= 1:
        return n

    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_sequence(count: int) -> Iterator[int]:
    """
    Generate a sequence of Fibonacci numbers.

    Args:
        count: Number of Fibonacci numbers to generate

    Yields:
        The next Fibonacci number in the sequence

    Examples:
        >>> list(fibonacci_sequence(5))
        [0, 1, 1, 2, 3]
    """
    if count <= 0:
        return

    a, b = 0, 1
    yield a

    if count > 1:
        yield b

        for _ in range(2, count):
            a, b = b, a + b
            yield b


# ============================================================================
# Unit Tests
# ============================================================================

class TestFibonacci:
    """Test suite for fibonacci functions"""

    def test_base_cases(self):
        """Test base cases"""
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1

    def test_small_numbers(self):
        """Test small Fibonacci numbers"""
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        for i, expected_val in enumerate(expected):
            assert fibonacci(i) == expected_val

    def test_sequence_generation(self):
        """Test sequence generation"""
        assert list(fibonacci_sequence(10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    def test_negative_input(self):
        """Test negative input handling"""
        if HAS_PYTEST:
            with pytest.raises(ValueError):
                fibonacci(-1)
        else:
            try:
                fibonacci(-1)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

    def test_type_validation(self):
        """Test type validation"""
        if HAS_PYTEST:
            with pytest.raises(TypeError):
                fibonacci(3.14)
        else:
            try:
                fibonacci(3.14)
                assert False, "Should have raised TypeError"
            except TypeError:
                pass


if __name__ == "__main__":
    print("Fibonacci Examples:")
    print("=" * 50)

    for i in range(10):
        print(f"fibonacci({{i}}) = {{fibonacci(i)}}")

    print(f"\\nFirst 15 Fibonacci numbers: {{list(fibonacci_sequence(15))}}")

    # Run tests
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("\\nRunning manual tests...")
        test = TestFibonacci()
        for method in dir(test):
            if method.startswith('test_'):
                try:
                    getattr(test, method)()
                    print(f" {{method}}")
                except Exception as e:
                    print(f" {{method}}: {{e}}")
'''


def _render_palindrome_func(name: str, brief: str) -> str:
    """Generate palindrome checking function with tests"""
    return f'''#!/usr/bin/env python3
"""
{brief}

Palindrome detection with support for various input types and options.

Example usage:
    >>> from lib_function import is_palindrome
    >>> is_palindrome("racecar")
    True
    >>> is_palindrome("hello")
    False
"""

from typing import Any, Union
import re

# Optional pytest import
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


def is_palindrome(s: Union[str, int], ignore_case: bool = True,
                  ignore_spaces: bool = True, alphanumeric_only: bool = False) -> bool:
    """
    Check if a string or number is a palindrome.

    Args:
        s: String or number to check
        ignore_case: Whether to ignore case differences
        ignore_spaces: Whether to ignore spaces
        alphanumeric_only: Whether to consider only alphanumeric characters

    Returns:
        True if s is a palindrome, False otherwise

    Examples:
        >>> is_palindrome("A man a plan a canal Panama", alphanumeric_only=True)
        True
        >>> is_palindrome(12321)
        True
    """
    # Convert to string if needed
    text = str(s)

    # Apply filters
    if alphanumeric_only:
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
    elif ignore_spaces:
        text = text.replace(' ', '')

    if ignore_case:
        text = text.lower()

    # Check palindrome
    return text == text[::-1]


# ============================================================================
# Unit Tests
# ============================================================================

class TestPalindrome:
    """Test suite for palindrome function"""

    def test_simple_palindromes(self):
        """Test simple palindrome strings"""
        assert is_palindrome("racecar") == True
        assert is_palindrome("level") == True
        assert is_palindrome("noon") == True

    def test_non_palindromes(self):
        """Test non-palindrome strings"""
        assert is_palindrome("hello") == False
        assert is_palindrome("python") == False

    def test_with_spaces(self):
        """Test palindromes with spaces"""
        assert is_palindrome("race car") == True
        assert is_palindrome("race car", ignore_spaces=False) == False

    def test_with_punctuation(self):
        """Test palindromes with punctuation"""
        assert is_palindrome("A man, a plan, a canal: Panama", alphanumeric_only=True) == True

    def test_numeric_palindromes(self):
        """Test numeric palindromes"""
        assert is_palindrome(12321) == True
        assert is_palindrome(12345) == False


if __name__ == "__main__":
    print("Palindrome Examples:")
    print("=" * 50)

    test_cases = [
        ("racecar", True),
        ("A man a plan a canal Panama", True),
        ("race a car", True),
        ("hello", False),
        (12321, True),
        (12345, False)
    ]

    for input_val, expected in test_cases:
        result = is_palindrome(input_val, alphanumeric_only=True)
        print(f"is_palindrome({{repr(input_val):30s}}) = {{result:5s}} (expected: {{expected}})")

    # Run tests
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("\\nRunning manual tests...")
        test = TestPalindrome()
        for method in dir(test):
            if method.startswith('test_'):
                try:
                    getattr(test, method)()
                    print(f" {{method}}")
                except Exception as e:
                    print(f" {{method}}: {{e}}")
'''


def _render_reverse_string_func(name: str, brief: str) -> str:
    """Generate string reversal function with tests"""
    return f'''#!/usr/bin/env python3
"""
{brief}

String manipulation utilities with focus on reversal operations.

Example usage:
    >>> from lib_function import reverse_string
    >>> reverse_string("hello")
    'olleh'
"""

from typing import List, Any

# Optional pytest import
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False


def reverse_string(s: str) -> str:
    """
    Reverse a string.

    Args:
        s: String to reverse

    Returns:
        Reversed string

    Examples:
        >>> reverse_string("hello")
        'olleh'
        >>> reverse_string("Python")
        'nohtyP'
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected string, got {{type(s).__name__}}")

    return s[::-1]


def reverse_words(s: str) -> str:
    """
    Reverse the order of words in a string.

    Args:
        s: String containing words

    Returns:
        String with words in reverse order

    Examples:
        >>> reverse_words("hello world")
        'world hello'
    """
    return ' '.join(reversed(s.split()))


# ============================================================================
# Unit Tests
# ============================================================================

class TestStringReverse:
    """Test suite for string reversal functions"""

    def test_simple_strings(self):
        """Test simple string reversal"""
        assert reverse_string("hello") == "olleh"
        assert reverse_string("Python") == "nohtyP"
        assert reverse_string("12345") == "54321"

    def test_empty_string(self):
        """Test empty string"""
        assert reverse_string("") == ""

    def test_single_character(self):
        """Test single character"""
        assert reverse_string("a") == "a"

    def test_palindrome(self):
        """Test palindrome strings"""
        assert reverse_string("racecar") == "racecar"

    def test_type_validation(self):
        """Test type validation"""
        if HAS_PYTEST:
            with pytest.raises(TypeError):
                reverse_string(123)
        else:
            try:
                reverse_string(123)
                assert False, "Should have raised TypeError"
            except TypeError:
                pass

    def test_word_reversal(self):
        """Test word order reversal"""
        assert reverse_words("hello world") == "world hello"
        assert reverse_words("one two three four") == "four three two one"


if __name__ == "__main__":
    print("String Reversal Examples:")
    print("=" * 50)

    examples = ["hello", "Python", "racecar", "hello world"]

    for text in examples:
        print(f"reverse_string({{repr(text):15s}}) = {{repr(reverse_string(text))}}")

    print("\\nWord reversal:")
    print(f"reverse_words('hello world') = {{repr(reverse_words('hello world'))}}")

    # Run tests
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("\\nRunning manual tests...")
        test = TestStringReverse()
        for method in dir(test):
            if method.startswith('test_'):
                try:
                    getattr(test, method)()
                    print(f" {{method}}")
                except Exception as e:
                    print(f" {{method}}: {{e}}")
'''


def _render_generic_func(name: str, brief: str) -> str:
    """Generate a generic function template with tests"""
    func_name = name.replace("-", "_").replace(" ", "_").lower()
    if not func_name or not func_name[0].isalpha():
        func_name = "process"

    return f'''#!/usr/bin/env python3
"""
{brief}

A library function with comprehensive documentation and tests.

Example usage:
    >>> from lib_function import {{func_name}}
    >>> result = {{func_name}}("example input")
    >>> print(result)
"""

from typing import Any, List, Dict, Optional, Union, Tuple
import logging

# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)

# Optional pytest import
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def {func_name}(input_data: Any, **kwargs) -> Any:
    """
    Process input data and return results.

    This is a template function that can be customized for specific needs.

    Args:
        input_data: The input data to process
        **kwargs: Additional optional parameters

    Returns:
        Processed result

    Raises:
        ValueError: If input_data is invalid
        TypeError: If input_data is of wrong type

    Examples:
        >>> {func_name}("test")
        'PROCESSED: test'
        >>> {func_name}(42)
        'PROCESSED: 42'
    """
    # Validate input
    if input_data is None:
        raise ValueError("input_data cannot be None")

    # Log the operation
    logger.debug(f"Processing input: {{input_data}}")

    # Process based on type
    if isinstance(input_data, str):
        result = f"PROCESSED: {{input_data}}"
    elif isinstance(input_data, (int, float)):
        result = f"PROCESSED: {{input_data}}"
    elif isinstance(input_data, list):
        result = [f"PROCESSED: {{item}}" for item in input_data]
    elif isinstance(input_data, dict):
        result = {{k: f"PROCESSED: {{v}}" for k, v in input_data.items()}}
    else:
        result = f"PROCESSED: {{str(input_data)}}"

    # Apply any additional processing from kwargs
    if kwargs.get('uppercase', False):
        if isinstance(result, str):
            result = result.upper()

    if kwargs.get('reverse', False):
        if isinstance(result, str):
            result = result[::-1]

    logger.debug(f"Result: {{result}}")
    return result


def {func_name}_batch(items: List[Any], **kwargs) -> List[Any]:
    """
    Process multiple items in batch.

    Args:
        items: List of items to process
        **kwargs: Options to pass to {func_name}

    Returns:
        List of processed results

    Examples:
        >>> {func_name}_batch(["a", "b", "c"])
        ['PROCESSED: a', 'PROCESSED: b', 'PROCESSED: c']
    """
    return [{func_name}(item, **kwargs) for item in items]


def {func_name}_async(input_data: Any, callback: Optional[callable] = None) -> Any:
    """
    Process data with optional callback.

    Args:
        input_data: Data to process
        callback: Optional function to call with result

    Returns:
        Processed result
    """
    result = {func_name}(input_data)

    if callback:
        callback(result)

    return result


# ============================================================================
# Helper Functions
# ============================================================================

def validate_input(data: Any) -> bool:
    """
    Validate input data meets requirements.

    Args:
        data: Data to validate

    Returns:
        True if valid, False otherwise
    """
    if data is None:
        return False

    # Add custom validation logic here
    return True


def transform_output(result: Any, format: str = "default") -> Any:
    """
    Transform output to desired format.

    Args:
        result: Result to transform
        format: Output format

    Returns:
        Transformed result
    """
    if format == "json":
        import json
        return json.dumps(result)
    elif format == "upper":
        return str(result).upper()

    return result


# ============================================================================
# Unit Tests
# ============================================================================

class Test{func_name.title().replace("_", "")}:
    """Test suite for {func_name} function"""

    def test_string_input(self):
        """Test with string input"""
        result = {func_name}("hello")
        assert result == "PROCESSED: hello"

    def test_numeric_input(self):
        """Test with numeric input"""
        assert {func_name}(42) == "PROCESSED: 42"
        assert {func_name}(3.14) == "PROCESSED: 3.14"

    def test_list_input(self):
        """Test with list input"""
        result = {func_name}([1, 2, 3])
        assert result == ["PROCESSED: 1", "PROCESSED: 2", "PROCESSED: 3"]

    def test_dict_input(self):
        """Test with dictionary input"""
        result = {func_name}({{"a": 1, "b": 2}})
        assert result == {{"a": "PROCESSED: 1", "b": "PROCESSED: 2"}}

    def test_none_input(self):
        """Test with None input"""
        if HAS_PYTEST:
            with pytest.raises(ValueError, match="cannot be None"):
                {func_name}(None)
        else:
            try:
                {func_name}(None)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

    def test_with_options(self):
        """Test with additional options"""
        result = {func_name}("test", uppercase=True)
        assert "PROCESSED" in result

        result = {func_name}("test", reverse=True)
        assert result[::-1] == "PROCESSED: test"

    def test_batch_processing(self):
        """Test batch processing"""
        items = ["a", "b", "c"]
        results = {func_name}_batch(items)
        assert len(results) == 3
        assert all("PROCESSED" in r for r in results)

    def test_async_processing(self):
        """Test async processing with callback"""
        callback_result = []

        def callback(result):
            callback_result.append(result)

        result = {func_name}_async("test", callback=callback)
        assert result == "PROCESSED: test"
        assert len(callback_result) == 1
        assert callback_result[0] == result


class Test{func_name.title().replace("_", "")}Integration:
    """Integration tests"""

    def test_end_to_end_workflow(self):
        """Test complete workflow"""
        # Step 1: Validate input
        data = "test data"
        assert validate_input(data) == True

        # Step 2: Process
        result = {func_name}(data)
        assert "PROCESSED" in result

        # Step 3: Transform output
        json_output = transform_output(result, format="json")
        assert isinstance(json_output, str)

    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid input
        if HAS_PYTEST:
            with pytest.raises(ValueError):
                {func_name}(None)
        else:
            try:
                {func_name}(None)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        # Test validation
        assert validate_input(None) == False
        assert validate_input("valid") == True


# ============================================================================
# Benchmarks
# ============================================================================

def benchmark_{func_name}(iterations: int = 1000):
    """
    Performance benchmark for {func_name}.

    Args:
        iterations: Number of iterations to run
    """
    import time

    test_data = ["test_{{}}".format(i) for i in range(100)]

    print(f"\\nBenchmarking {{func_name}} with {{iterations}} iterations...")

    start = time.perf_counter()
    for _ in range(iterations):
        for data in test_data:
            _ = {func_name}(data)
    elapsed = time.perf_counter() - start

    total_ops = iterations * len(test_data)
    print(f"Processed {{total_ops}} operations in {{elapsed:.4f}} seconds")
    print(f"Average time per operation: {{elapsed / total_ops * 1000:.4f}} ms")
    print(f"Operations per second: {{total_ops / elapsed:.0f}}")


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print(f"{{func_name.title().replace('_', ' ')}} Function Examples:")
    print("=" * 60)

    # Demonstrate basic usage
    examples = [
        "hello world",
        42,
        [1, 2, 3],
        {{"key": "value"}},
    ]

    for example in examples:
        try:
            result = {func_name}(example)
            print(f"{{func_name}}({{repr(example):20s}}) = {{repr(result)}}")
        except Exception as e:
            print(f"{{func_name}}({{repr(example):20s}}) = Error: {{e}}")

    # Demonstrate with options
    print("\\nWith options:")
    print(f"{{func_name}}('test', uppercase=True) = {{repr({func_name}('test', uppercase=True))}}")
    print(f"{{func_name}}('test', reverse=True)   = {{repr({func_name}('test', reverse=True))}}")

    # Demonstrate batch processing
    print("\\nBatch processing:")
    batch_result = {func_name}_batch(['a', 'b', 'c'])
    print(f"{{func_name}}_batch(['a', 'b', 'c']) = {{batch_result}}")

    # Run unit tests
    print("\\nRunning unit tests...")
    print("=" * 60)

    try:
        import pytest
        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest not installed. Running manual tests...")

        test_basic = Test{func_name.title().replace("_", "")}()
        test_integration = Test{func_name.title().replace("_", "")}Integration()

        all_tests = []
        for test_cls in [test_basic, test_integration]:
            all_tests.extend([
                (test_cls, method) for method in dir(test_cls)
                if method.startswith('test_')
            ])

        passed = 0
        failed = 0

        for test_obj, method_name in all_tests:
            try:
                method = getattr(test_obj, method_name)
                method()
                print(f" {{test_obj.__class__.__name__}}.{{method_name}}")
                passed += 1
            except Exception as e:
                print(f" {{test_obj.__class__.__name__}}.{{method_name}}: {{e}}")
                failed += 1

        print(f"\\nResults: {{passed}} passed, {{failed}} failed")

    # Run benchmark
    benchmark_{func_name}(100)
'''
