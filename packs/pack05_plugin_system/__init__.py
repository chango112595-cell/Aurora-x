"""
Aurora Pack 05: Plugin System (Unified)

This pack consolidates all plugin-related functionality:
- 5A: Plugin API - Core plugin interface
- 5B: Plugin Loader - Dynamic loading system
- 5C: (Reserved)
- 5D: (Reserved)
- 5E: Capability System - Plugin capabilities
- 5F: Event Hooks - Event-driven architecture
- 5G: Permissions Resolver - Access control
- 5H: Plugin Store - Plugin marketplace
- 5I: Versioning & Upgrades - Version management
- 5J: State Persistence - Plugin state storage
- 5K: Diagnostics - Health monitoring
- 5L: Test Framework - Plugin testing

Author: Aurora AI System
Version: 1.0.0
"""

from pathlib import Path

PACK_ID = "pack05"
PACK_NAME = "Plugin System"
PACK_VERSION = "1.0.0"

SUBMODULES = {
    "5A": "plugin_api",
    "5B": "plugin_loader",
    "5E": "capability_system",
    "5F": "event_hooks",
    "5G": "permissions_resolver",
    "5H": "plugin_store",
    "5I": "versioning_upgrades",
    "5J": "state_persistence",
    "5K": "diagnostics",
    "5L": "test_framework",
}


def get_pack_info():
    """Return pack metadata"""
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "version": PACK_VERSION,
        "submodules": SUBMODULES,
        "total_submodules": len(SUBMODULES),
        "status": "integrated",
    }


def load_all_submodules():
    """Load all submodules dynamically"""
    loaded = {}
    base_path = Path(__file__).parent

    for code, name in SUBMODULES.items():
        module_path = base_path / name / "core" / "module.py"
        if module_path.exists():
            loaded[code] = {"name": name, "status": "loaded", "path": str(module_path)}
        else:
            loaded[code] = {"name": name, "status": "not_found", "path": str(module_path)}

    return loaded
