#!/usr/bin/env python3
"""
Aurora's Personal Debugging Toolkit
Quick utilities for debugging any issue
"""

import json
import logging
import traceback
from datetime import datetime
from functools import wraps
from pathlib import Path


class AuroraDebugger:
    """Aurora's debugging utilities"""

    def __init__(self):
        self.debug_log = Path("/workspaces/Aurora-x/.aurora_knowledge/debug_sessions.jsonl")
        self.debug_log.parent.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(Path("/workspaces/Aurora-x/.aurora_knowledge/aurora_debug.log")),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("AuroraDebugger")

    def debug_print(self, *args, **kwargs):
        """Enhanced print debugging"""
        import inspect

        frame = inspect.currentframe().f_back
        filename = frame.f_code.co_filename
        line = frame.f_lineno
        function = frame.f_code.co_name

        print(f"🔍 [{filename}:{line} in {function}()]")
        print("   ", *args, **kwargs)

    def trace_calls(self, func):
        """Decorator to trace function calls"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.debug(f"CALL {func.__name__}({args}, {kwargs})")
            try:
                result = func(*args, **kwargs)
                self.logger.debug(f"RETURN {func.__name__} = {result}")
                return result
            except Exception as e:
                self.logger.error(f"ERROR {func.__name__}: {e}")
                raise

        return wrapper

    def time_it(self, func):
        """Decorator to time function execution"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            self.logger.info(f"⏱️  {func.__name__} took {elapsed:.4f}s")
            return result

        return wrapper

    def safe_execute(self, func, *args, **kwargs):
        """Execute with comprehensive error handling"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Exception in {func.__name__}:")
            self.logger.error(f"  Type: {type(e).__name__}")
            self.logger.error(f"  Message: {str(e)}")
            self.logger.error("  Traceback:")
            traceback.print_exc()

            # Log to file
            error_entry = {
                "timestamp": datetime.now().isoformat(),
                "function": func.__name__,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
            }

            with open(self.debug_log, "a") as f:
                f.write(json.dumps(error_entry) + "\n")

            return None

    def inspect_object(self, obj, name="object"):
        """Thoroughly inspect any object"""
        print(f"\n🔍 Inspecting {name}:")
        print(f"   Type: {type(obj)}")
        print(f"   Value: {obj}")
        print(f"   Dir: {[x for x in dir(obj) if not x.startswith('_')]}")

        if hasattr(obj, "__dict__"):
            print(f"   Attributes: {obj.__dict__}")

    def check_types(self, **variables):
        """Check types of multiple variables"""
        print("\n📊 Type Check:")
        for name, value in variables.items():
            print(f"   {name}: {type(value).__name__} = {value}")

    def breakpoint_here(self, condition=True):
        """Conditional breakpoint"""
        if condition:
            self.logger.warning("⚠️  Breakpoint hit!")
            breakpoint()


# Global instance for easy access
aurora_debug = AuroraDebugger()

# Convenience functions
dprint = aurora_debug.debug_print
trace = aurora_debug.trace_calls
time_it = aurora_debug.time_it
safe = aurora_debug.safe_execute
inspect = aurora_debug.inspect_object
check_types = aurora_debug.check_types

if __name__ == "__main__":
    print("🧰 Aurora's Debug Toolkit loaded!")
    print("\nAvailable tools:")
    print("  dprint()       - Enhanced debug printing")
    print("  @trace         - Trace function calls")
    print("  @time_it       - Time function execution")
    print("  safe()         - Safe execution with error handling")
    print("  inspect(obj)   - Inspect any object")
    print("  check_types()  - Check variable types")
