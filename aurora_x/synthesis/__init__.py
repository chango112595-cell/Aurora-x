"""
Aurora-X Synthesis Module
Exports the Universal Code Synthesis Engine and its components
"""

from .universal_engine import (
    BlueprintEngine,
    DynamicSynthesizer,
    # Core components
    MultiIntentParser,
    ParsedIntent,
    PersistenceLayer,
    # Data structures
    ProjectType,
    SafetyGate,
    # Main synthesis function
    synthesize_universal,
    synthesize_universal_sync,
)

# Version info
__version__ = "1.0.0"
__author__ = "Aurora-X Team"

# Default exports
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
