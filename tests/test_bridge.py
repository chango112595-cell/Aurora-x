"""
NexusBridge Test Suite
Ensures NexusBridge can import and execute loaded modules dynamically.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_nexus_bridge_imports():
    """Verify NexusBridge can be imported."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    assert NexusBridge is not None


def test_nexus_bridge_init():
    """Verify NexusBridge initializes correctly."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    
    bridge = NexusBridge()
    
    assert hasattr(bridge, 'modules'), "Bridge should have modules dict"
    assert hasattr(bridge, 'modules_by_id'), "Bridge should have modules_by_id dict"
    assert hasattr(bridge, 'pool'), "Bridge should have thread pool"


def test_module_bridge_loads():
    """Ensures all 550 modules load with proper APIs."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    
    bridge = NexusBridge()
    result = bridge.load_modules()
    
    assert "loaded" in result, "Result should contain 'loaded' count"
    assert result["loaded"] == 550, f"Expected 550 modules, found {result['loaded']}"
    assert len(bridge.modules) == 550, f"Expected 550 modules in dict, found {len(bridge.modules)}"
    
    for name, module in bridge.modules.items():
        assert hasattr(module, 'execute'), f"Module {name} missing execute method"
        assert callable(module.execute), f"Module {name} execute is not callable"


def test_sample_module_exec():
    """Verifies that module execution returns structured results."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    
    bridge = NexusBridge()
    bridge.load_modules()
    
    module = bridge.get_module(1)
    assert module is not None, "Module 1 not found"
    
    result = module.execute({"task": "semantic-summary"})
    
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "status" in result, "Result should contain 'status'"
    assert result["status"] == "success", f"Expected success status, got {result['status']}"


def test_module_lifecycle_hooks():
    """Verify modules have all lifecycle hooks."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    
    bridge = NexusBridge()
    bridge.load_modules()
    
    for module_id in [1, 101, 250, 550]:
        module = bridge.get_module(module_id)
        assert module is not None, f"Module {module_id} not found"
        
        assert hasattr(module, 'on_boot'), f"Module {module_id} missing on_boot"
        assert hasattr(module, 'on_tick'), f"Module {module_id} missing on_tick"
        assert hasattr(module, 'on_reflect'), f"Module {module_id} missing on_reflect"
        assert hasattr(module, 'execute'), f"Module {module_id} missing execute"


def test_bridge_execute_all():
    """Verify execute_all runs across all modules."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    
    bridge = NexusBridge()
    bridge.load_modules()
    
    results = bridge.execute_all({"task": "test"})
    
    assert isinstance(results, list), "Results should be a list"
    assert len(results) == 550, f"Expected 550 results, got {len(results)}"


def test_bridge_status():
    """Verify bridge status reporting."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    
    bridge = NexusBridge()
    bridge.load_modules()
    
    status = bridge.get_status()
    
    assert "initialized" in status, "Status should contain initialized flag"
    assert "total_modules" in status, "Status should contain total_modules"
    assert status["initialized"] is True, "Bridge should be initialized"
    assert status["total_modules"] == 550, f"Expected 550 modules, got {status['total_modules']}"


def test_bridge_shutdown():
    """Verify bridge shuts down gracefully."""
    from aurora_nexus_v3.core.nexus_bridge import NexusBridge
    
    bridge = NexusBridge()
    bridge.load_modules()
    
    assert bridge._initialized is True
    
    bridge.shutdown()
    
    assert bridge._initialized is False
    assert len(bridge.modules) == 0
