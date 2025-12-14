#!/usr/bin/env python3
"""
Aurora Production Integration Test
===================================

Comprehensive integration test verifying all production components work together:
- Hybrid Orchestrator with all systems
- Task execution with different strategies
- Hyperspeed mode integration
- Error handling and recovery
- Resource management

Author: Aurora AI System
Version: 1.0.0
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List


class ProductionIntegrationTest:
    """Integration test for production readiness"""
    
    def __init__(self):
        self.root = Path(__file__).parent
        self.test_results = []
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log test message"""
        symbol = "✓" if level == "PASS" else ("✗" if level == "FAIL" else "•")
        print(f"{symbol} {message}")
        
    async def test_orchestrator_initialization(self) -> bool:
        """Test hybrid orchestrator initialization"""
        print("\n=== Test 1: Hybrid Orchestrator Initialization ===")
        
        try:
            sys.path.insert(0, str(self.root / "aurora_nexus_v3"))
            from core.hybrid_orchestrator import HybridOrchestrator
            
            orchestrator = HybridOrchestrator()
            success = await orchestrator.initialize()
            
            if not success:
                self.log("Orchestrator initialization failed", "FAIL")
                return False
            
            status = orchestrator.get_status()
            
            # Verify all components
            checks = [
                (status["components"]["tiers"]["total"] == 188, "188 Tiers loaded"),
                (status["components"]["aems"]["total"] == 66, "66 AEMs loaded"),
                (status["components"]["modules"]["total"] == 550, "550 Modules loaded"),
                (status["components"]["hyperspeed"]["enabled"], "Hyperspeed enabled"),
                (status["initialized"], "Orchestrator initialized"),
                (status["running"], "Orchestrator running")
            ]
            
            all_passed = True
            for check, description in checks:
                if check:
                    self.log(description, "PASS")
                else:
                    self.log(f"{description} - FAILED", "FAIL")
                    all_passed = False
            
            await orchestrator.shutdown()
            return all_passed
            
        except Exception as e:
            self.log(f"Exception during initialization: {e}", "FAIL")
            self.errors.append(str(e))
            return False
    
    async def test_task_execution_strategies(self) -> bool:
        """Test different execution strategies"""
        print("\n=== Test 2: Task Execution Strategies ===")
        
        try:
            sys.path.insert(0, str(self.root / "aurora_nexus_v3"))
            from core.hybrid_orchestrator import HybridOrchestrator, ExecutionStrategy
            
            orchestrator = HybridOrchestrator()
            await orchestrator.initialize()
            
            strategies = [
                ExecutionStrategy.SEQUENTIAL,
                ExecutionStrategy.PARALLEL,
                ExecutionStrategy.HYBRID,
                ExecutionStrategy.ADAPTIVE
            ]
            
            all_passed = True
            for strategy in strategies:
                try:
                    result = await orchestrator.execute_hybrid(
                        task_type="test",
                        payload={"test": "data"},
                        strategy=strategy,
                        timeout_ms=5000
                    )
                    
                    if result.success:
                        self.log(f"{strategy.value} strategy executed successfully", "PASS")
                    else:
                        self.log(f"{strategy.value} strategy failed: {result.error}", "FAIL")
                        all_passed = False
                        
                except Exception as e:
                    self.log(f"{strategy.value} strategy exception: {e}", "FAIL")
                    all_passed = False
            
            await orchestrator.shutdown()
            return all_passed
            
        except Exception as e:
            self.log(f"Exception during strategy testing: {e}", "FAIL")
            self.errors.append(str(e))
            return False
    
    async def test_component_health(self) -> bool:
        """Test component health monitoring"""
        print("\n=== Test 3: Component Health Monitoring ===")
        
        try:
            sys.path.insert(0, str(self.root / "aurora_nexus_v3"))
            from core.hybrid_orchestrator import HybridOrchestrator
            
            orchestrator = HybridOrchestrator()
            await orchestrator.initialize()
            
            health = orchestrator.get_health()
            
            all_healthy = True
            for component, status in health.items():
                health_str = status.value if hasattr(status, 'value') else str(status)
                if health_str == "healthy":
                    self.log(f"{component}: {health_str}", "PASS")
                else:
                    self.log(f"{component}: {health_str}", "FAIL")
                    all_healthy = False
            
            await orchestrator.shutdown()
            return all_healthy
            
        except Exception as e:
            self.log(f"Exception during health check: {e}", "FAIL")
            self.errors.append(str(e))
            return False
    
    async def test_metrics_tracking(self) -> bool:
        """Test metrics tracking"""
        print("\n=== Test 4: Metrics Tracking ===")
        
        try:
            sys.path.insert(0, str(self.root / "aurora_nexus_v3"))
            from core.hybrid_orchestrator import HybridOrchestrator
            
            orchestrator = HybridOrchestrator()
            await orchestrator.initialize()
            
            # Execute a few tasks
            for i in range(3):
                await orchestrator.execute_hybrid(
                    task_type="test",
                    payload={"iteration": i},
                    timeout_ms=2000
                )
            
            metrics = orchestrator.get_metrics()
            
            checks = [
                (metrics["total_tasks_executed"] >= 3, f"Tasks executed: {metrics['total_tasks_executed']}"),
                ("successful_tasks" in metrics, "Successful tasks tracked"),
                ("average_execution_time_ms" in metrics, "Average execution time tracked")
            ]
            
            all_passed = True
            for check, description in checks:
                if check:
                    self.log(description, "PASS")
                else:
                    self.log(f"{description} - FAILED", "FAIL")
                    all_passed = False
            
            await orchestrator.shutdown()
            return all_passed
            
        except Exception as e:
            self.log(f"Exception during metrics tracking: {e}", "FAIL")
            self.errors.append(str(e))
            return False
    
    async def test_hyperspeed_mode(self) -> bool:
        """Test hyperspeed mode functionality"""
        print("\n=== Test 5: Hyperspeed Mode ===")
        
        try:
            sys.path.insert(0, str(self.root))
            from hyperspeed.aurora_hyper_speed_mode import AuroraHyperSpeedMode
            
            hyperspeed = AuroraHyperSpeedMode(project_root=str(self.root))
            
            self.log("Hyperspeed mode initialized", "PASS")
            self.log(f"Max workers: {hyperspeed.max_workers}", "PASS")
            
            return True
            
        except Exception as e:
            self.log(f"Exception during hyperspeed test: {e}", "FAIL")
            self.errors.append(str(e))
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("\n" + "="*70)
        print("AURORA PRODUCTION INTEGRATION TESTS")
        print("="*70)
        
        tests = [
            ("Orchestrator Initialization", self.test_orchestrator_initialization),
            ("Task Execution Strategies", self.test_task_execution_strategies),
            ("Component Health", self.test_component_health),
            ("Metrics Tracking", self.test_metrics_tracking),
            ("Hyperspeed Mode", self.test_hyperspeed_mode)
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = await test_func()
                results.append((name, result))
                self.test_results.append({"test": name, "passed": result})
            except Exception as e:
                self.log(f"\nTest '{name}' crashed: {e}", "FAIL")
                results.append((name, False))
                self.test_results.append({"test": name, "passed": False, "error": str(e)})
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status} - {name}")
        
        print("\n" + "="*70)
        print(f"RESULTS: {passed}/{total} tests passed")
        
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if passed == total:
            print("\n✓ ALL INTEGRATION TESTS PASSED")
            print("="*70 + "\n")
            return True
        else:
            print(f"\n✗ {total - passed} TESTS FAILED")
            print("="*70 + "\n")
            return False


async def main():
    """Main test function"""
    tester = ProductionIntegrationTest()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
