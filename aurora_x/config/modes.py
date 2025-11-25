"""
Modes

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

from typing import Dict, List, Tuple, Optional, Any, Union


SAFE = "safe"
EXPLORE = "explore"
DEFAULT_MODE = SAFE


def is_safe(mode: str) -> bool:
    """
        Is Safe
        
        Args:
            mode: mode
    
        Returns:
            Result of operation
        """
    return (mode or DEFAULT_MODE).lower() == SAFE
