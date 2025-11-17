#!/usr/bin/env python3
"""
test

A library function with comprehensive documentation and tests.

Example usage:
    >>> from lib_function import {func_name}
    >>> result = {func_name}("example input")
    >>> print(result)
"""

import logging
from typing import Any

# Function name for templates
func_name = "test_function"
# Optional pytest import
try:
    import pytest

    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test(input_data: Any, **kwargs) -> Any:
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
        >>> test("test")
        'PROCESSED: test'
        >>> test(42)
        'PROCESSED: 42'
    """
    # Validate input
    if input_data is None:
        raise ValueError("input_data cannot be None")

    # Log the operation
    logger.debug("Processing input: {input_data}")

    # Process based on type
    if isinstance(input_data, str):
        result = f"PROCESSED: {input_data}"
    elif isinstance(input_data, (int, float)):
        result = f"PROCESSED: {input_data}"
    elif isinstance(input_data, list):
        result = [f"PROCESSED: {item}" for item in input_data]
    elif isinstance(input_data, dict):
        result = {k: f"PROCESSED: {v}" for k, v in input_data.items()}
    else:
        result = f"PROCESSED: {str(input_data)}"

    # Apply any additional processing from kwargs
    if kwargs.get("uppercase", False):
        if isinstance(result, str):
            result = result.upper()

    if kwargs.get("reverse", False):
        if isinstance(result, str):
            result = result[::-1]

    logger.debug("Result: {result}")
    return result


def test_batch(items: list[Any], **kwargs) -> list[Any]:
    """
    Process multiple items in batch.

    Args:
        items: List of items to process
        **kwargs: Options to pass to test

    Returns:
        List of processed results

    Examples:
        >>> test_batch(["a", "b", "c"])
        ['PROCESSED: a', 'PROCESSED: b', 'PROCESSED: c']
    """
    return [test(item, **kwargs) for item in items]


def test_async(input_data: Any, callback: callable | None = None) -> Any:
    """
    Process data with optional callback.

    Args:
        input_data: Data to process
        callback: Optional function to call with result

    Returns:
        Processed result
    """
    result = test(input_data)

    if callback is not None:
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


def transform_output(result: Any, output_format: str = "default") -> Any:
    """
    Transform output to desired format.

    Args:
        result: Result to transform
        output_format: Output format

    Returns:
        Transformed result
    """
    if output_format == "json":
        import json

        return json.dumps(result)
    elif output_format == "upper":
        return str(result).upper()

    return result


# ============================================================================
# Unit Tests
# ============================================================================


class TestTest:
    """Test suite for test function"""

    def test_string_input(self):
        """Test with string input"""
        result = test("hello")
        assert result == "PROCESSED: hello"

    def test_numeric_input(self):
        """Test with numeric input"""
        assert test(42) == "PROCESSED: 42"
        assert test(3.14) == "PROCESSED: 3.14"

    def test_list_input(self):
        """Test with list input"""
        result = test([1, 2, 3])
        assert result == ["PROCESSED: 1", "PROCESSED: 2", "PROCESSED: 3"]

    def test_dict_input(self):
        """Test with dictionary input"""
        result = test({"a": 1, "b": 2})
        assert result == {"a": "PROCESSED: 1", "b": "PROCESSED: 2"}

    def test_none_input(self):
        """Test with None input"""
        if HAS_PYTEST:
            with pytest.raises(ValueError, match="cannot be None"):
                test(None)
        else:
            try:
                test(None)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

    def test_with_options(self):
        """Test with additional options"""
        result = test("test", uppercase=True)
        assert "PROCESSED" in result

        result = test("test", reverse=True)
        assert result[::-1] == "PROCESSED: test"

    def test_batch_processing(self):
        """Test batch processing"""
        items = ["a", "b", "c"]
        results = test_batch(items)
        assert len(results) == 3
        assert all("PROCESSED" in r for r in results)

    def test_async_processing(self):
        """Test async processing with callback"""
        callback_result = []

        def callback(result):
            callback_result.append(result)

        result = test_async("test", callback=callback)
        assert result == "PROCESSED: test"
        assert len(callback_result) == 1
        assert callback_result[0] == result


class TestTestIntegration:
    """Integration tests"""

    def test_end_to_end_workflow(self):
        """Test complete workflow"""
        # Step 1: Validate input
        data = "test data"
        assert validate_input(data)

        # Step 2: Process
        result = test(data)
        assert "PROCESSED" in result

        # Step 3: Transform output
        json_output = transform_output(result, output_format="json")
        assert isinstance(json_output, str)

    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid input
        if HAS_PYTEST:
            with pytest.raises(ValueError):
                test(None)
        else:
            try:
                test(None)
                assert False, "Should have raised ValueError"
            except ValueError:
                pass

        # Test validation
        assert not validate_input(None)
        assert validate_input("valid")


# ============================================================================
# Benchmarks
# ============================================================================


def benchmark_test(iterations: int = 1000):
    """
    Performance benchmark for test.

    Args:
        iterations: Number of iterations to run
    """
    import time

    test_data = [f"test_{i}" for i in range(100)]

    print(f"\nBenchmarking {func_name} with {iterations} iterations...")

    start = time.perf_counter()
    for _ in range(iterations):
        for data in test_data:
            _ = test(data)
    elapsed = time.perf_counter() - start

    total_ops = iterations * len(test_data)
    print(f"Processed {total_ops} operations in {elapsed:.4f} seconds")
    print(f"Average time per operation: {elapsed / total_ops * 1000:.4f} ms")
    print(f"Operations per second: {total_ops / elapsed:.0f}")


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    print(f"{func_name.title().replace('_', ' ')} Function Examples:")
    print("=" * 60)

    # Demonstrate basic usage
    examples = [
        "hello world",
        42,
        [1, 2, 3],
        {"key": "value"},
    ]

    for example in examples:
        try:
            demo_result = test(example)
            print(f"{func_name}({repr(example):20s}) = {repr(demo_result)}")
        except Exception as e:
            print(f"{func_name}({repr(example):20s}) = Error: {e}")

    # Demonstrate with options
    print("\nWith options:")
    print(f"{func_name}('test', uppercase=True) = {repr(test('test', uppercase=True))}")
    print(f"{func_name}('test', reverse=True)   = {repr(test('test', reverse=True))}")

    # Demonstrate batch processing
    print("\nBatch processing:")
    batch_result = test_batch(["a", "b", "c"])
    print(f"{func_name}_batch(['a', 'b', 'c']) = {batch_result}")

    # Run unit tests
    print("\nRunning unit tests...")
    print("=" * 60)

    try:
        import pytest

        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest not installed. Running manual tests...")

        test_basic = TestTest()
        test_integration = TestTestIntegration()

        all_tests = []
        for test_cls in [test_basic, test_integration]:
            all_tests.extend([(test_cls, method) for method in dir(test_cls) if method.startswith("test_")])

        passed = 0
        failed = 0

        for test_obj, method_name in all_tests:
            try:
                method = getattr(test_obj, method_name)
                method()
                print(f"✓ {test_obj.__class__.__name__}.{method_name}")
                passed += 1
            except Exception as e:
                print(f"✗ {test_obj.__class__.__name__}.{method_name}: {e}")
                failed += 1

        print(f"\nResults: {passed} passed, {failed} failed")

    # Run benchmark
    benchmark_test(100)
