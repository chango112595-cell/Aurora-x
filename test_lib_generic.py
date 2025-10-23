#!/usr/bin/env python3
"""
create a data processing function

A library function with comprehensive documentation and tests.

Example usage:
    >>> from lib_function import {func_name}
    >>> result = {func_name}("example input")
    >>> print(result)
"""

import logging
from typing import Any

import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_a_data_processing_fun(input_data: Any, **kwargs) -> Any:
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
        >>> create_a_data_processing_fun("test")
        'PROCESSED: test'
        >>> create_a_data_processing_fun(42)
        'PROCESSED: 42'
    """
    # Validate input
    if input_data is None:
        raise ValueError("input_data cannot be None")

    # Log the operation
    logger.debug(f"Processing input: {input_data}")

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

    logger.debug(f"Result: {result}")
    return result


def create_a_data_processing_fun_batch(items: list[Any], **kwargs) -> list[Any]:
    """
    Process multiple items in batch.

    Args:
        items: List of items to process
        **kwargs: Options to pass to create_a_data_processing_fun

    Returns:
        List of processed results

    Examples:
        >>> create_a_data_processing_fun_batch(["a", "b", "c"])
        ['PROCESSED: a', 'PROCESSED: b', 'PROCESSED: c']
    """
    return [create_a_data_processing_fun(item, **kwargs) for item in items]


def create_a_data_processing_fun_async(input_data: Any, callback: callable | None = None) -> Any:
    """
    Process data with optional callback.

    Args:
        input_data: Data to process
        callback: Optional function to call with result

    Returns:
        Processed result
    """
    result = create_a_data_processing_fun(input_data)

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


class TestCreateADataProcessingFun:
    """Test suite for create_a_data_processing_fun function"""

    def test_string_input(self):
        """Test with string input"""
        result = create_a_data_processing_fun("hello")
        assert result == "PROCESSED: hello"

    def test_numeric_input(self):
        """Test with numeric input"""
        assert create_a_data_processing_fun(42) == "PROCESSED: 42"
        assert create_a_data_processing_fun(3.14) == "PROCESSED: 3.14"

    def test_list_input(self):
        """Test with list input"""
        result = create_a_data_processing_fun([1, 2, 3])
        assert result == ["PROCESSED: 1", "PROCESSED: 2", "PROCESSED: 3"]

    def test_dict_input(self):
        """Test with dictionary input"""
        result = create_a_data_processing_fun({"a": 1, "b": 2})
        assert result == {"a": "PROCESSED: 1", "b": "PROCESSED: 2"}

    def test_none_input(self):
        """Test with None input"""
        with pytest.raises(ValueError, match="cannot be None"):
            create_a_data_processing_fun(None)

    def test_with_options(self):
        """Test with additional options"""
        result = create_a_data_processing_fun("test", uppercase=True)
        assert "PROCESSED" in result

        result = create_a_data_processing_fun("test", reverse=True)
        assert result[::-1] == "PROCESSED: test"

    def test_batch_processing(self):
        """Test batch processing"""
        items = ["a", "b", "c"]
        results = create_a_data_processing_fun_batch(items)
        assert len(results) == 3
        assert all("PROCESSED" in r for r in results)

    def test_async_processing(self):
        """Test async processing with callback"""
        callback_result = []

        def callback(result):
            callback_result.append(result)

        result = create_a_data_processing_fun_async("test", callback=callback)
        assert result == "PROCESSED: test"
        assert len(callback_result) == 1
        assert callback_result[0] == result


class TestCreateADataProcessingFunIntegration:
    """Integration tests"""

    def test_end_to_end_workflow(self):
        """Test complete workflow"""
        # Step 1: Validate input
        data = "test data"
        assert validate_input(data)

        # Step 2: Process
        result = create_a_data_processing_fun(data)
        assert "PROCESSED" in result

        # Step 3: Transform output
        json_output = transform_output(result, format="json")
        assert isinstance(json_output, str)

    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid input
        with pytest.raises(ValueError):
            create_a_data_processing_fun(None)

        # Test validation
        assert not validate_input(None)
        assert validate_input("valid")


# ============================================================================
# Benchmarks
# ============================================================================


def benchmark_create_a_data_processing_fun(iterations: int = 1000):
    """
    Performance benchmark for create_a_data_processing_fun.

    Args:
        iterations: Number of iterations to run
    """
    import time

    test_data = [f"test_{i}" for i in range(100)]

    print(f"\nBenchmarking {func_name} with {iterations} iterations...")

    start = time.perf_counter()
    for _ in range(iterations):
        for data in test_data:
            _ = create_a_data_processing_fun(data)
    elapsed = time.perf_counter() - start

    total_ops = iterations * len(test_data)
    print(f"Processed {total_ops} operations in {elapsed:.4f} seconds")
    print(f"Average time per operation: {elapsed / total_ops * 1000:.4f} ms")
    print(f"Operations per second: {total_ops / elapsed:.0f}")


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    func_name = "create_a_data_processing_fun"
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
            result = create_a_data_processing_fun(example)
            print(f"{func_name}({repr(example):20s}) = {repr(result)}")
        except Exception as e:
            print(f"{func_name}({repr(example):20s}) = Error: {e}")

    # Demonstrate with options
    print("\nWith options:")
    result_upper = create_a_data_processing_fun("test", uppercase=True)
    print(f"{func_name}('test', uppercase=True) = {repr(result_upper)}")
    result_reverse = create_a_data_processing_fun("test", reverse=True)
    print(f"{func_name}('test', reverse=True)   = {repr(result_reverse)}")

    # Demonstrate batch processing
    print("\nBatch processing:")
    batch_result = create_a_data_processing_fun_batch(["a", "b", "c"])
    print(f"{func_name}_batch(['a', 'b', 'c']) = {batch_result}")

    # Run unit tests
    print("\nRunning unit tests...")
    print("=" * 60)

    try:
        import pytest

        pytest.main([__file__, "-v", "--tb=short"])
    except ImportError:
        print("pytest not installed. Running manual tests...")

        test_basic = TestCreateADataProcessingFun()
        test_integration = TestCreateADataProcessingFunIntegration()

        all_tests = []
        for test_cls in [test_basic, test_integration]:
            all_tests.extend(
                [(test_cls, method) for method in dir(test_cls) if method.startswith("test_")]
            )

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
    benchmark_create_a_data_processing_fun(100)
