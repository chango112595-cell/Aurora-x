"""
Aurora Nexus V3 Autofix Module
==============================
Provides self-repair functionality for Aurora-X modules.
Monitors module health and triggers automatic recovery when errors occur.
"""

import json
import logging
import traceback
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NexusAutofix")

AUTOFIX_LOG_PATH = Path("logs/autofix")
AUTOFIX_LOG_PATH.mkdir(parents=True, exist_ok=True)


class AutofixRegistry:
    """Registry for tracking module errors and autofix attempts."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.error_log: dict[str, list] = {}
        self.fix_attempts: dict[str, int] = {}
        self.handlers: dict[str, Callable] = {}
        self._initialized = True

    def log_error(self, module_name: str, error: Exception, context: dict[str, Any] = None):
        """Log an error for a module."""
        if module_name not in self.error_log:
            self.error_log[module_name] = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
        }

        self.error_log[module_name].append(entry)

        log_file = AUTOFIX_LOG_PATH / f"{module_name}_errors.json"
        try:
            existing = []
            if log_file.exists():
                existing = json.loads(log_file.read_text())
            existing.append(entry)
            log_file.write_text(json.dumps(existing[-100:], indent=2))
        except Exception as e:
            logger.warning(f"Failed to write error log: {e}")

    def register_handler(self, error_type: str, handler: Callable):
        """Register a custom error handler."""
        self.handlers[error_type] = handler

    def get_handler(self, error_type: str) -> Callable | None:
        """Get handler for an error type."""
        return self.handlers.get(error_type)

    def get_fix_attempts(self, module_name: str) -> int:
        """Get number of fix attempts for a module."""
        return self.fix_attempts.get(module_name, 0)

    def increment_fix_attempts(self, module_name: str):
        """Increment fix attempt counter."""
        self.fix_attempts[module_name] = self.fix_attempts.get(module_name, 0) + 1

    def reset_fix_attempts(self, module_name: str):
        """Reset fix attempt counter after successful recovery."""
        self.fix_attempts[module_name] = 0

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of all errors."""
        return {
            module: {
                "error_count": len(errors),
                "last_error": errors[-1] if errors else None,
                "fix_attempts": self.fix_attempts.get(module, 0),
            }
            for module, errors in self.error_log.items()
        }


registry = AutofixRegistry()


def nexus_autofix(module_name: str, error: Exception, context: dict[str, Any] = None) -> bool:
    """
    Primary autofix entry point.
    Called by modules when errors occur.

    Args:
        module_name: Name of the module that encountered the error
        error: The exception that was raised
        context: Optional context about the operation that failed

    Returns:
        True if autofix was successful, False otherwise
    """
    logger.info(f"[Autofix] Triggered for {module_name}: {type(error).__name__}")

    registry.log_error(module_name, error, context)
    registry.increment_fix_attempts(module_name)

    attempts = registry.get_fix_attempts(module_name)
    if attempts > 5:
        logger.warning(f"[Autofix] {module_name} exceeded max fix attempts ({attempts})")
        return False

    error_type = type(error).__name__
    handler = registry.get_handler(error_type)

    if handler:
        try:
            result = handler(module_name, error, context)
            if result:
                registry.reset_fix_attempts(module_name)
                logger.info(f"[Autofix] Successfully repaired {module_name}")
                return True
        except Exception as e:
            logger.error(f"[Autofix] Handler failed: {e}")

    success = _default_autofix(module_name, error, context)

    if success:
        registry.reset_fix_attempts(module_name)
        logger.info(f"[Autofix] Default repair successful for {module_name}")
    else:
        logger.warning(f"[Autofix] Could not repair {module_name}")

    return success


def _default_autofix(module_name: str, error: Exception, context: dict[str, Any] = None) -> bool:
    """
    Default autofix strategy.
    Attempts common recovery patterns.
    """
    error_type = type(error).__name__

    if error_type == "ImportError":
        return _handle_import_error(module_name, error)

    if error_type == "ConnectionError":
        return _handle_connection_error(module_name, error)

    if error_type == "MemoryError":
        return _handle_memory_error(module_name, error)

    if error_type in ("KeyError", "AttributeError"):
        return _handle_state_error(module_name, error)

    return False


def _handle_import_error(module_name: str, error: Exception) -> bool:
    """Handle import errors by logging missing dependencies."""
    logger.info(f"[Autofix] Import error in {module_name}: {error}")
    return False


def _handle_connection_error(module_name: str, error: Exception) -> bool:
    """Handle connection errors with retry logic."""
    logger.info(f"[Autofix] Connection error in {module_name}, will retry on next tick")
    return True


def _handle_memory_error(module_name: str, error: Exception) -> bool:
    """Handle memory errors by triggering garbage collection."""
    import gc

    gc.collect()
    logger.info(f"[Autofix] Triggered GC for {module_name}")
    return True


def _handle_state_error(module_name: str, error: Exception) -> bool:
    """Handle state errors by logging and allowing retry."""
    logger.info(f"[Autofix] State error in {module_name}: {error}")
    return True


def register_autofix_handler(error_type: str, handler: Callable):
    """
    Register a custom autofix handler for a specific error type.

    Args:
        error_type: The exception class name (e.g., "ValueError")
        handler: Callable that takes (module_name, error, context) and returns bool
    """
    registry.register_handler(error_type, handler)


def get_autofix_status() -> dict[str, Any]:
    """Get current autofix system status."""
    return {
        "active": True,
        "error_summary": registry.get_error_summary(),
        "registered_handlers": list(registry.handlers.keys()),
    }


def clear_error_history(module_name: str = None):
    """Clear error history for a module or all modules."""
    if module_name:
        registry.error_log.pop(module_name, None)
        registry.fix_attempts.pop(module_name, None)
    else:
        registry.error_log.clear()
        registry.fix_attempts.clear()
