"""
Aurora-X Synthesis Module
Exports the Universal Code Synthesis Engine and its components
"""
from typing import Dict, List, Tuple, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor

from .universal_engine import (
    BlueprintEngine,
    DynamicSynthesizer,
    MultiIntentParser,
    ParsedIntent,
    PersistenceLayer,
    ProjectType,
    SafetyGate,
    synthesize_universal,
    synthesize_universal_sync,
)

__version__ = "1.0.0"
__author__ = "Aurora-X Team"

__all__ = [
    "synthesize_universal",
    "synthesize_universal_sync",
    "MultiIntentParser",
    "BlueprintEngine",
    "DynamicSynthesizer",
    "SafetyGate",
    "PersistenceLayer",
    "ProjectType",
    "ParsedIntent",
]
