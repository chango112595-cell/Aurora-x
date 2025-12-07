"""
Aurora Packs - Unified Pack System

All Aurora packs consolidated and integrated:
- Pack 01: Core System
- Pack 02: Environment Profiler
- Pack 03: OS Base + EdgeOS Runtimes (3A-3J)
- Pack 04: Launcher
- Pack 05: Plugin System (5A-5L)
- Pack 06: Firmware System
- Pack 07: Secure Signing
- Pack 08: Conversational Engine
- Pack 09: Compute Layer
- Pack 10: Autonomy Engine
- Pack 11: Device Mesh
- Pack 12: Toolforge
- Pack 13: Runtime 2
- Pack 14: Hardware Abstraction
- Pack 15: Intel Fabric

Author: Aurora AI System
Version: 1.0.0
"""

from pathlib import Path
import importlib.util

PACKS = {
    "pack01": {"name": "Core System", "dir": "pack01_pack01"},
    "pack02": {"name": "Environment Profiler", "dir": "pack02_env_profiler"},
    "pack03": {"name": "OS Base + EdgeOS", "dir": "pack03_os_edge", "submodules": ["3A", "3B", "3C", "3D", "3E", "3F", "3G", "3H", "3I", "3J"]},
    "pack04": {"name": "Launcher", "dir": "pack04_launcher"},
    "pack05": {"name": "Plugin System", "dir": "pack05_plugin_system", "submodules": ["5A", "5B", "5E", "5F", "5G", "5H", "5I", "5J", "5K", "5L"]},
    "pack06": {"name": "Firmware System", "dir": "pack06_firmware_system"},
    "pack07": {"name": "Secure Signing", "dir": "pack07_secure_signing"},
    "pack08": {"name": "Conversational Engine", "dir": "pack08_conversational_engine"},
    "pack09": {"name": "Compute Layer", "dir": "pack09_compute_layer"},
    "pack10": {"name": "Autonomy Engine", "dir": "pack10_autonomy_engine"},
    "pack11": {"name": "Device Mesh", "dir": "pack11_device_mesh"},
    "pack12": {"name": "Toolforge", "dir": "pack12_toolforge"},
    "pack13": {"name": "Runtime 2", "dir": "pack13_runtime_2"},
    "pack14": {"name": "Hardware Abstraction", "dir": "pack14_hw_abstraction"},
    "pack15": {"name": "Intel Fabric", "dir": "pack15_intel_fabric"}
}

def get_all_packs():
    """Return information about all packs"""
    base_path = Path(__file__).parent
    result = {}
    
    for pack_id, info in PACKS.items():
        pack_dir = base_path / info["dir"]
        exists = pack_dir.exists()
        submodules = info.get("submodules", [])
        
        result[pack_id] = {
            "name": info["name"],
            "directory": info["dir"],
            "exists": exists,
            "submodules": submodules,
            "submodule_count": len(submodules) if submodules else 0
        }
    
    return result

def load_pack(pack_id: str):
    """Load a specific pack by ID"""
    if pack_id not in PACKS:
        return None
    
    info = PACKS[pack_id]
    base_path = Path(__file__).parent
    pack_dir = base_path / info["dir"]
    
    init_file = pack_dir / "__init__.py"
    if init_file.exists():
        spec = importlib.util.spec_from_file_location(pack_id, init_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    
    return None

def get_pack_summary():
    """Get a summary of all packs for display"""
    packs = get_all_packs()
    total = len(packs)
    loaded = sum(1 for p in packs.values() if p["exists"])
    submodules = sum(p["submodule_count"] for p in packs.values())
    
    return {
        "total_packs": total,
        "loaded_packs": loaded,
        "total_submodules": submodules,
        "packs": packs
    }

# Auto-load summary on import
_summary = None

def get_summary():
    global _summary
    if _summary is None:
        _summary = get_pack_summary()
    return _summary
