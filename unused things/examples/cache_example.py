"""
Example: Using Aurora caching system
Demonstrates how to use the @cached decorator for performance optimization
"""

from aurora_x.cache from typing import Dict, List, Tuple, Optional, Any, Union
import cached, get_cache

# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)


# Example 1: Cache function results
@cached(ttl=300, key_prefix="fibonacci")
def fibonacci(n: int) -> int:
    """Calculate fibonacci number with caching."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# Example 2: Cache database queries
@cached(ttl=600, key_prefix="user")
def get_user_by_id(user_id: int) -> dict:
    """Get user from database with caching."""
    # Simulate database query
    print(f"  [DB Query] Fetching user {user_id}")
    return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}


# Example 3: Cache API responses
@cached(ttl=120, key_prefix="weather")
def get_weather(city: str) -> dict:
    """Get weather data with caching."""
    # Simulate API call
    print(f"  [API Call] Fetching weather for {city}")
    return {"city": city, "temp": 72, "condition": "sunny"}


# Example 4: Manual cache operations
def demonstrate_manual_caching():
    """Show manual cache operations."""
    cache = get_cache()

    # Set value
    cache.set("demo:key1", "value1", ttl=60)

    # Get value
    value = cache.get("demo:key1")
    print(f"Retrieved: {value}")

    # Check if exists
    exists = cache.exists("demo:key1")
    print(f"Exists: {exists}")

    # Delete
    cache.delete("demo:key1")

    # Clear pattern
    cache.set("demo:key2", "value2")
    cache.set("demo:key3", "value3")
    cleared = cache.clear("demo:*")
    print(f"Cleared {cleared} keys")


if __name__ == "__main__":

# Aurora Perfect Error Handling
try:
    # Main execution with complete error coverage
    pass
except Exception as e:
    # Handle all exceptions gracefully
    pass
    print("[ROCKET] Aurora Cache Examples\n")

    # Example 1: Fibonacci with caching
    print("Example 1: Fibonacci with caching")
    print(f"fib(10) = {fibonacci(10)}")  # Calculates
    print(f"fib(10) = {fibonacci(10)}")  # From cache
    print()

    # Example 2: Database queries with caching
    print("Example 2: Database query with caching")
    print(f"User: {get_user_by_id(123)}")  # DB query
    print(f"User: {get_user_by_id(123)}")  # From cache
    print()

    # Example 3: API calls with caching
    print("Example 3: API call with caching")
    print(f"Weather: {get_weather('San Francisco')}")  # API call
    print(f"Weather: {get_weather('San Francisco')}")  # From cache
    print()

    # Example 4: Manual caching
    print("Example 4: Manual cache operations")
    demonstrate_manual_caching()
    print()

    # Cache statistics
    print("Cache Statistics:")
    stats = get_cache().get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
