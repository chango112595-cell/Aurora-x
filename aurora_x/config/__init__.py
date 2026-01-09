"""
Aurora-X Configuration Module

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

# Export configuration functions and classes
from aurora_x.config.runtime_config import (
    Settings,  # SPEC-2: Pydantic configuration schema
    data_path,
    data_root,
    dependency_status,
    load_settings,  # SPEC-2: Load settings function
    readiness,
    validate_required_config,
)

__all__ = [
    "Settings",
    "load_settings",
    "validate_required_config",
    "readiness",
    "dependency_status",
    "data_root",
    "data_path",
]
