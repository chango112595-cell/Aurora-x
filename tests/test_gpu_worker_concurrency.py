"""
GPU + Worker Concurrency Test Suite (Stage G)
Extended tests for hybrid mode and autonomous worker engine stability under heavy load.
"""
import sys
import os
import time
import threading
import concurrent.futures
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGPUReadiness:
    """GPU availability and readiness tests."""
    
    def test_gpu_availability_detection(self):
        """Verify GPU availability is correctly detected."""
        try:
            import torch
            gpu_available = torch.cuda.is_available()
            
            if gpu_available:
                device_count = torch.cuda.device_count()
                assert device_count > 0, "GPU detected but device count is 0"
                
                device_name = torch.cuda.get_device_name(0)
                assert device_name is not None, "GPU name should be available"
            else:
                pass
                
        except ImportError:
            pass
    
    def test_bridge_gpu_flag_consistency(self):
        """Verify NexusBridge GPU flag matches system state."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        
        try:
            import torch
            expected = torch.cuda.is_available()
        except ImportError:
            expected = False
        
        assert bridge.gpu_available == expected, \
            f"Bridge GPU flag ({bridge.gpu_available}) doesn't match system ({expected})"
    
    def test_gpu_modules_identified(self):
        """Verify GPU-enabled modules (451-550) are correctly identified."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        bridge.load_modules()
        
        gpu_modules = []
        for module_id in range(451, 551):
            module = bridge.get_module(module_id)
            if module and hasattr(module, 'requires_gpu') and module.requires_gpu:
                gpu_modules.append(module_id)
        
        bridge.shutdown()
    
    def test_gpu_fallback_execution(self):
        """Verify GPU modules fallback to CPU when GPU unavailable."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        bridge.load_modules()
        
        module = bridge.get_module(500)
        assert module is not None, "Module 500 should exist"
        
        result = module.execute({"task": "gpu-fallback-test"})
        assert result["status"] == "success", "GPU module should execute (with CPU fallback)"
        
        bridge.shutdown()


class TestWorkerPoolConcurrency:
    """Worker pool concurrency and stress tests."""
    
    def test_thread_pool_initialization(self):
        """Verify thread pool initializes correctly."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge(pool_size=8)
        
        assert bridge.pool is not None, "Thread pool should be initialized"
        assert bridge.pool._max_workers == 8, "Pool should have 8 workers"
        
        bridge.shutdown()
    
    def test_concurrent_module_execution(self):
        """Test concurrent execution across multiple modules."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge(pool_size=16)
        bridge.load_modules()
        
        module_ids = list(range(1, 101))
        results = []
        errors = []
        
        def execute_module(mid):
            try:
                module = bridge.get_module(mid)
                if module:
                    return module.execute({"task": f"concurrent-test-{mid}"})
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = {executor.submit(execute_module, mid): mid for mid in module_ids}
            
            for future in concurrent.futures.as_completed(futures, timeout=60):
                mid = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    if result.get("status") != "success":
                        errors.append((mid, result))
                except Exception as e:
                    errors.append((mid, str(e)))
        
        assert len(results) == 100, f"Expected 100 results, got {len(results)}"
        assert len(errors) == 0, f"Concurrent execution had {len(errors)} errors"
        
        bridge.shutdown()
    
    def test_worker_spawn_and_terminate(self):
        """Ensure workers spawn and terminate correctly."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge(pool_size=32)
        bridge.load_modules()
        
        results = bridge.execute_all({"task": "worker-spawn-test"})
        
        assert len(results) == 550, f"Expected 550 results, got {len(results)}"
        
        bridge.shutdown()
        
        assert bridge._initialized is False, "Bridge should be shut down"
    
    def test_heavy_load_execution(self):
        """Test system under heavy load with multiple iterations."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge(pool_size=16)
        bridge.load_modules()
        
        iterations = 5
        total_executions = 0
        errors = 0
        
        for i in range(iterations):
            results = bridge.execute_all({"task": f"heavy-load-{i}", "iteration": i})
            total_executions += len(results)
            errors += sum(1 for r in results if r.get("status") != "success")
        
        expected = 550 * iterations
        assert total_executions == expected, \
            f"Expected {expected} executions, got {total_executions}"
        assert errors == 0, f"Heavy load test had {errors} errors"
        
        bridge.shutdown()
    
    def test_parallel_bridge_instances(self):
        """Test multiple bridge instances running in parallel."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridges = []
        results = []
        
        def run_bridge(bridge_id):
            bridge = NexusBridge(pool_size=4)
            bridge.load_modules()
            result = bridge.execute(1, {"task": f"parallel-bridge-{bridge_id}"})
            bridge.shutdown()
            return result
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_bridge, i) for i in range(3)]
            
            for future in concurrent.futures.as_completed(futures, timeout=60):
                results.append(future.result())
        
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert all(r["status"] == "success" for r in results), "All bridges should succeed"


class TestMemoryFabricSemanticSearch:
    """Memory Fabric semantic search regression tests."""
    
    def test_semantic_search_endpoint(self):
        """Verify semantic search endpoint works."""
        import socket
        import requests
        
        def is_port_open(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    return s.connect_ex(('127.0.0.1', port)) == 0
            except:
                return False
        
        if not is_port_open(5004):
            return
        
        r = requests.post(
            "http://localhost:5004/message",
            json={"role": "user", "content": "Test semantic memory entry", "importance": 0.9},
            timeout=5
        )
        assert r.status_code == 200
        
        r = requests.post(
            "http://localhost:5004/search",
            json={"query": "semantic memory", "top_k": 5},
            timeout=5
        )
        assert r.status_code == 200
        
        body = r.json()
        assert "success" in body
        assert "results" in body
    
    def test_memory_fabric_integrity(self):
        """Verify memory fabric data integrity."""
        import socket
        import requests
        
        def is_port_open(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    return s.connect_ex(('127.0.0.1', port)) == 0
            except:
                return False
        
        if not is_port_open(5004):
            return
        
        r = requests.get("http://localhost:5004/integrity", timeout=5)
        
        assert r.status_code == 200
        body = r.json()
        assert body.get("success") is True
        assert "integrity" in body
    
    def test_fact_storage_and_recall(self):
        """Test fact storage and recall functionality."""
        import socket
        import requests
        
        def is_port_open(port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    return s.connect_ex(('127.0.0.1', port)) == 0
            except:
                return False
        
        if not is_port_open(5004):
            return
        
        test_key = f"test_fact_{int(time.time())}"
        test_value = "Aurora-X Ultra test value"
        
        r = requests.post(
            "http://localhost:5004/fact",
            json={"key": test_key, "value": test_value, "category": "test"},
            timeout=5
        )
        assert r.status_code == 200
        
        r = requests.post(
            "http://localhost:5004/recall",
            json={"key": test_key},
            timeout=5
        )
        assert r.status_code == 200
        body = r.json()
        assert body.get("value") == test_value


class TestHybridModeStability:
    """Hybrid mode (CPU + GPU) stability tests."""
    
    def test_hybrid_mode_under_stress(self):
        """Test hybrid mode stability under stress."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge(pool_size=16)
        bridge.load_modules()
        
        for i in range(3):
            result = bridge.execute_hybrid({
                "task": "stress-test",
                "iteration": i,
                "data": list(range(100))
            })
            
            assert result["status"] == "success", f"Iteration {i} failed"
            assert result["modules_executed"] == 550
        
        bridge.shutdown()
    
    def test_hybrid_mode_recovery(self):
        """Test hybrid mode recovers from simulated failures."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge()
        bridge.load_modules()
        
        result = bridge.execute_hybrid({"task": "recovery-test"})
        assert result["status"] == "success"
        
        bridge.shutdown()
        
        bridge2 = NexusBridge()
        bridge2.load_modules()
        
        result2 = bridge2.execute_hybrid({"task": "post-recovery-test"})
        assert result2["status"] == "success"
        
        bridge2.shutdown()
    
    def test_lifecycle_hooks_under_load(self):
        """Test lifecycle hooks remain stable under load."""
        from aurora_nexus_v3.core.nexus_bridge import NexusBridge
        
        bridge = NexusBridge(pool_size=16)
        bridge.load_modules()
        
        for i in range(10):
            bridge.on_tick({"tick": i, "timestamp": time.time()})
        
        reflections = bridge.on_reflect({"context": "load-test"})
        assert len(reflections) == 550, f"Expected 550 reflections, got {len(reflections)}"
        
        for reflection in reflections[:10]:
            assert "module" in reflection
            assert "metrics" in reflection
            assert "healthy" in reflection
        
        bridge.shutdown()
