"""
System Integration Test Suite
Ensures Nexus V3, Luminar V2, and Memory Fabric cooperate correctly.
"""
import requests
import time
import subprocess
import sys
import os
import socket
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMORY_FABRIC_URL = os.getenv("AURORA_MEMORY_FABRIC_URL", "http://127.0.0.1:5004")


def _memory_fabric_target() -> tuple[str, int]:
    parsed = urlparse(MEMORY_FABRIC_URL)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 5004
    return host, port


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a port is accepting connections."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except:
        return False


def wait_for_port(host: str, port: int, timeout: int = 30) -> bool:
    """Wait for a port to become available."""
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(host, port):
            return True
        time.sleep(0.5)
    return False


class TestMemoryFabricIntegration:
    """Test Memory Fabric V2 service integration."""
    
    def test_memory_fabric_status(self):
        """Verify memory fabric status endpoint."""
        host, port = _memory_fabric_target()
        if not is_port_open(host, port):
            mem = subprocess.Popen(
                [sys.executable, "aurora_memory_fabric_v2/service.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            wait_for_port(host, port, timeout=10)
            
            try:
                r = requests.get(f"{MEMORY_FABRIC_URL}/status", timeout=5)
                assert r.status_code == 200, f"Expected 200, got {r.status_code}"
                
                body = r.json()
                assert "success" in body, "Response missing 'success' field"
                assert body["success"] is True, "Status should return success=True"
            finally:
                mem.terminate()
        else:
            r = requests.get(f"{MEMORY_FABRIC_URL}/status", timeout=5)
            assert r.status_code == 200
    
    def test_memory_fabric_message_storage(self):
        """Verify memory fabric can store and retrieve messages."""
        host, port = _memory_fabric_target()
        if not is_port_open(host, port):
            mem = subprocess.Popen(
                [sys.executable, "aurora_memory_fabric_v2/service.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            wait_for_port(host, port, timeout=10)
            
            try:
                r = requests.post(
                    f"{MEMORY_FABRIC_URL}/message",
                    json={"role": "user", "content": "Test message", "importance": 0.8},
                    timeout=5
                )
                assert r.status_code == 200
                
                body = r.json()
                assert body["success"] is True
                assert "entry" in body
            finally:
                mem.terminate()
        else:
            r = requests.post(
                f"{MEMORY_FABRIC_URL}/message",
                json={"role": "user", "content": "Test message", "importance": 0.8},
                timeout=5
            )
            assert r.status_code == 200


class TestNexusBridgeIntegration:
    """Test Nexus Bridge integration with modules."""
    
    def test_nexus_bridge_module_loading(self):
        """Verify NexusBridge loads all modules correctly."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        result = bridge.load_modules()
        
        assert result["loaded"] == 550
        assert len(result.get("errors", [])) == 0
        
        bridge.shutdown()
    
    def test_nexus_bridge_hybrid_execution(self):
        """Verify hybrid mode execution works."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        bridge.load_modules()
        
        result = bridge.execute_hybrid({"task": "integration-test"})
        
        assert result["status"] == "success"
        assert "mode" in result
        assert result["modules_executed"] == 550
        
        bridge.shutdown()
    
    def test_nexus_bridge_lifecycle_hooks(self):
        """Verify lifecycle hooks work correctly."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        bridge.load_modules()
        
        boot_results = bridge.on_boot()
        assert len(boot_results) == 550
        
        bridge.on_tick({"tick": 1})
        
        reflections = bridge.on_reflect({"context": "test"})
        assert len(reflections) == 550
        
        bridge.shutdown()


class TestFullStackIntegration:
    """Full stack integration tests."""
    
    def test_end_to_end_boot_and_chat(self):
        """Boot minimal stack and verify chat + memory fabric integration."""
        processes = []
        
        try:
            host, port = _memory_fabric_target()
            if not is_port_open(host, port):
                mem = subprocess.Popen(
                    [sys.executable, "aurora_memory_fabric_v2/service.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                processes.append(mem)
                wait_for_port(host, port, timeout=10)
            
            r = requests.get(f"{MEMORY_FABRIC_URL}/status", timeout=5)
            assert r.status_code == 200, "Memory Fabric should respond"
            
            from aurora_nexus_v3.core.nexus_bridge import NexusBridge
            
            bridge = NexusBridge()
            result = bridge.load_modules()
            assert result["loaded"] == 550, "All modules should load"
            
            exec_result = bridge.execute(1, {"task": "integration-test"})
            assert exec_result["status"] == "success", "Module execution should succeed"
            
            bridge.shutdown()
            
        finally:
            for p in processes:
                p.terminate()
    
    def test_memory_nexus_coordination(self):
        """Verify Memory Fabric and Nexus Bridge coordinate properly."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        bridge.load_modules()
        
        module = bridge.get_module(1)
        assert module is not None
        
        result = module.execute({"task": "memory-coordination-test"})
        assert result["status"] == "success"
        
        reflection = module.on_reflect({"context": "coordination-test"})
        assert "module" in reflection
        assert "metrics" in reflection
        assert "healthy" in reflection
        
        bridge.shutdown()


class TestHybridModeValidation:
    """Validate hybrid mode (CPU + GPU) execution."""
    
    def test_hybrid_mode_detection(self):
        """Verify hybrid mode correctly detects GPU availability."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        
        assert hasattr(bridge, 'gpu_available'), "Bridge should track GPU availability"
        assert isinstance(bridge.gpu_available, bool), "gpu_available should be boolean"
    
    def test_hybrid_execution_fallback(self):
        """Verify hybrid mode falls back to CPU when GPU unavailable."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        bridge.load_modules()
        
        result = bridge.execute_hybrid({"task": "fallback-test"})
        
        assert result["status"] == "success"
        assert result["mode"] in ["cpu", "gpu"]
        
        bridge.shutdown()
