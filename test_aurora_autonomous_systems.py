#!/usr/bin/env python3
"""
Aurora Integration Test Suite
Tests all 6 phases of autonomous evolution completed in <1 hour

Tests:
1. Self-Monitoring System
2. Tier Expansion Detection
3. Tier Orchestration
4. Performance Optimization
5. Full Autonomy Engine
6. Strategic Planning
"""

import sys
from pathlib import Path
from datetime import datetime


class AuroraIntegrationTester:
    """Comprehensive test suite for Aurora's new autonomous systems"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def test_phase_1_self_monitoring(self):
        """Test Phase 1: Self-Monitoring System"""
        print("\n" + "="*60)
        print("🧪 TESTING PHASE 1: SELF-MONITORING")
        print("="*60)

        try:
            from aurora_self_monitor import AuroraSelfMonitor

            # Test 1: Initialization
            print("\n  Test 1.1: Initialize monitor...")
            monitor = AuroraSelfMonitor()
            monitor.initialize()
            assert monitor.aurora.total_capabilities == 54, "Should have 54 capabilities"
            assert monitor.file_count > 0, "Should monitor files"
            print("    ✅ Monitor initialized successfully")

            # Test 2: Health monitoring
            print("\n  Test 1.2: System health check...")
            health = monitor.monitor_system_health()
            assert 'cpu_percent' in health, "Should track CPU"
            assert 'memory_percent' in health, "Should track memory"
            assert health['status'] in ['OPTIMAL',
                                        'WARNING', 'CRITICAL'], "Should have status"
            print(
                f"    ✅ Health: {health['status']}, CPU: {health['cpu_percent']:.1f}%, Memory: {health['memory_percent']:.1f}%")

            # Test 3: Performance metrics
            print("\n  Test 1.3: Performance metrics...")
            metrics = monitor.get_performance_metrics()
            assert metrics['aurora_capabilities']['total'] == 54, "Should track 54 capabilities"
            print(
                f"    ✅ Metrics collected: {len(metrics['system_health'])} data points")

            # Test 4: Dashboard generation
            print("\n  Test 1.4: Dashboard generation...")
            dashboard = monitor.generate_dashboard()
            assert 'AURORA SELF-MONITOR DASHBOARD' in dashboard, "Should generate dashboard"
            assert '54' in dashboard, "Should show capability count"
            print("    ✅ Dashboard generated successfully")

            self.results.append({"phase": "Phase 1", "status": "PASS"})
            self.passed += 1
            print("\n✅ PHASE 1: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"\n❌ PHASE 1 FAILED: {e}")
            self.results.append(
                {"phase": "Phase 1", "status": "FAIL", "error": str(e)})
            self.failed += 1
            return False

    def test_phase_2_tier_expansion(self):
        """Test Phase 2: Tier Expansion System"""
        print("\n" + "="*60)
        print("🧪 TESTING PHASE 2: TIER EXPANSION")
        print("="*60)

        try:
            from aurora_tier_expansion import AuroraTierDetector, AuroraTierBuilder

            # Test 1: Pattern detection
            print("\n  Test 2.1: Codebase pattern analysis...")
            detector = AuroraTierDetector()
            patterns = detector.analyze_codebase()
            assert isinstance(
                patterns, dict), "Should return pattern dictionary"
            assert len(patterns) > 0, "Should detect patterns"
            print(f"    ✅ Detected {len(patterns)} pattern types")

            # Test 2: Gap identification
            print("\n  Test 2.2: Capability gap identification...")
            gaps = detector.identify_gaps()
            assert isinstance(gaps, list), "Should return list of gaps"
            print(f"    ✅ Identified {len(gaps)} capability gaps")

            # Test 3: Tier specification generation
            if gaps:
                print("\n  Test 2.3: Tier specification generation...")
                spec = detector.generate_tier_spec(gaps[0])
                assert 'tier_name' in spec, "Should have tier name"
                assert 'tier_number' in spec, "Should have tier number"
                assert 'skills' in spec, "Should define skills"
                print(
                    f"    ✅ Generated spec for Tier {spec['tier_number']}: {spec['tier_name']}")

            # Test 4: Code generation
            print("\n  Test 2.4: Tier code generation...")
            builder = AuroraTierBuilder()
            if gaps:
                spec = detector.generate_tier_spec(gaps[0])
                code = builder.build_tier_code(spec)
                assert 'def _get_tier_' in code, "Should generate method"
                assert spec['tier_name'].lower(
                ) in code.lower(), "Should include tier name"
                print(f"    ✅ Generated {len(code)} characters of Python code")

            self.results.append({"phase": "Phase 2", "status": "PASS"})
            self.passed += 1
            print("\n✅ PHASE 2: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"\n❌ PHASE 2 FAILED: {e}")
            self.results.append(
                {"phase": "Phase 2", "status": "FAIL", "error": str(e)})
            self.failed += 1
            return False

    def test_phase_3_tier_orchestration(self):
        """Test Phase 3: Tier Orchestration"""
        print("\n" + "="*60)
        print("🧪 TESTING PHASE 3: TIER ORCHESTRATION")
        print("="*60)

        try:
            from aurora_tier_orchestrator import AuroraTierOrchestrator

            # Test 1: Problem analysis
            print("\n  Test 3.1: Problem analysis...")
            orchestrator = AuroraTierOrchestrator()
            analysis = orchestrator.analyze_problem(
                "Fix pylint errors autonomously")
            assert 'required_tiers' in analysis, "Should identify required tiers"
            assert 'complexity' in analysis, "Should determine complexity"
            print(
                f"    ✅ Analysis: {analysis['complexity']} complexity, {analysis['tier_count']} tiers needed")

            # Test 2: Tier selection
            print("\n  Test 3.2: Optimal tier selection...")
            tiers = orchestrator.select_optimal_tiers(analysis)
            assert isinstance(tiers, list), "Should return list of tiers"
            print(f"    ✅ Selected {len(tiers)} optimal tiers")

            # Test 3: Execution
            print("\n  Test 3.3: Tier combination execution...")
            result = orchestrator.execute_tier_combination(tiers, "Test task")
            assert result['success'], "Execution should succeed"
            assert 'execution_time' in result, "Should track execution time"
            print(f"    ✅ Executed in {result['execution_time']:.4f}s")

            # Test 4: Knowledge synthesis
            print("\n  Test 3.4: Knowledge synthesis...")
            synthesis = orchestrator.synthesize_knowledge([result])
            assert synthesis['success_rate'] > 0, "Should have success rate"
            print(f"    ✅ Success rate: {synthesis['success_rate']*100:.0f}%")

            # Test 5: Learning
            print("\n  Test 3.5: Learning from execution...")
            orchestrator.learn_from_execution(result)
            assert len(
                orchestrator.success_patterns) > 0, "Should learn patterns"
            print(
                f"    ✅ Learned {len(orchestrator.success_patterns)} patterns")

            self.results.append({"phase": "Phase 3", "status": "PASS"})
            self.passed += 1
            print("\n✅ PHASE 3: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"\n❌ PHASE 3 FAILED: {e}")
            self.results.append(
                {"phase": "Phase 3", "status": "FAIL", "error": str(e)})
            self.failed += 1
            return False

    def test_phase_4_performance_optimization(self):
        """Test Phase 4: Performance Optimization"""
        print("\n" + "="*60)
        print("🧪 TESTING PHASE 4: PERFORMANCE OPTIMIZATION")
        print("="*60)

        try:
            from aurora_performance_optimizer import AuroraPredictor, AuroraPerformanceOptimizer

            # Test 1: Predictor initialization
            print("\n  Test 4.1: Issue predictor...")
            predictor = AuroraPredictor()
            predictor.load_historical_data()
            assert len(
                predictor.historical_issues) > 0, "Should load historical data"
            print(
                f"    ✅ Loaded {len(predictor.historical_issues)} historical patterns")

            # Test 2: Pattern analysis
            print("\n  Test 4.2: Pattern analysis...")
            patterns = predictor.analyze_patterns()
            assert 'most_common_issues' in patterns, "Should identify common issues"
            print(
                f"    ✅ Analyzed {len(patterns['most_common_issues'])} issue types")

            # Test 3: Issue prediction
            print("\n  Test 4.3: Issue prediction...")
            predictions = predictor.predict_issues()
            assert isinstance(predictions, list), "Should return predictions"
            print(f"    ✅ Generated {len(predictions)} predictions")

            # Test 4: Performance profiling
            print("\n  Test 4.4: Performance profiling...")
            optimizer = AuroraPerformanceOptimizer()
            profile = optimizer.profile_system()
            assert 'operations' in profile, "Should profile operations"
            assert 'total_profile_time' in profile, "Should track profile time"
            print(
                f"    ✅ Profiled {len(profile['operations'])} operations in {profile['total_profile_time']:.4f}s")

            # Test 5: Bottleneck detection
            print("\n  Test 4.5: Bottleneck detection...")
            bottlenecks = optimizer.identify_bottlenecks(profile)
            print(f"    ✅ Identified {len(bottlenecks)} bottlenecks")

            self.results.append({"phase": "Phase 4", "status": "PASS"})
            self.passed += 1
            print("\n✅ PHASE 4: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"\n❌ PHASE 4 FAILED: {e}")
            self.results.append(
                {"phase": "Phase 4", "status": "FAIL", "error": str(e)})
            self.failed += 1
            return False

    def test_phase_5_full_autonomy(self):
        """Test Phase 5: Full Autonomy"""
        print("\n" + "="*60)
        print("🧪 TESTING PHASE 5: FULL AUTONOMY")
        print("="*60)

        try:
            from aurora_full_autonomy import AuroraAutonomyEngine, AuroraSelfImprover

            # Test 1: Confidence assessment
            print("\n  Test 5.1: Confidence assessment...")
            autonomy = AuroraAutonomyEngine()
            confidence = autonomy.assess_confidence(
                "Fix pylint errors", {'tier_count': 3, 'historical_success': 0.9})
            assert 0.0 <= confidence <= 1.0, "Confidence should be between 0 and 1"
            print(f"    ✅ Confidence: {confidence*100:.0f}%")

            # Test 2: Autonomous decision
            print("\n  Test 5.2: Autonomous decision making...")
            decision = autonomy.make_autonomous_decision(
                "Test task", confidence)
            assert 'decision' in decision, "Should make decision"
            assert 'reasoning' in decision, "Should provide reasoning"
            print(f"    ✅ Decision: {decision['decision']}")

            # Test 3: Approval gate removal
            print("\n  Test 5.3: Approval gate removal...")
            removed = autonomy.remove_approval_gate('code_quality_fixes')
            assert removed, "Should remove safe gate"
            print(
                f"    ✅ Removed gate, total: {autonomy.approval_gates_removed}")

            # Test 4: Autonomy level
            print("\n  Test 5.4: Autonomy level calculation...")
            level = autonomy.calculate_autonomy_level()
            assert 0.0 <= level <= 1.0, "Autonomy level should be 0-1"
            print(f"    ✅ Autonomy level: {level*100:.0f}%")

            # Test 5: Self-improvement
            print("\n  Test 5.5: Self-improvement analysis...")
            improver = AuroraSelfImprover()
            analysis = improver.analyze_own_code()
            assert isinstance(analysis, list), "Should return analysis list"
            print(f"    ✅ Analyzed {len(analysis)} Aurora files")

            self.results.append({"phase": "Phase 5", "status": "PASS"})
            self.passed += 1
            print("\n✅ PHASE 5: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"\n❌ PHASE 5 FAILED: {e}")
            self.results.append(
                {"phase": "Phase 5", "status": "FAIL", "error": str(e)})
            self.failed += 1
            return False

    def test_phase_6_strategic_planning(self):
        """Test Phase 6: Strategic Planning"""
        print("\n" + "="*60)
        print("🧪 TESTING PHASE 6: STRATEGIC PLANNING")
        print("="*60)

        try:
            from aurora_strategist import AuroraContextEngine, AuroraStrategist

            # Test 1: Context analysis
            print("\n  Test 6.1: Codebase context analysis...")
            context_engine = AuroraContextEngine()
            context = context_engine.analyze_codebase_context()
            assert 'project_name' in context, "Should identify project"
            assert context['capabilities'] == 54, "Should track capabilities"
            print(
                f"    ✅ Project: {context['project_name']}, {context['total_files']} Python files")

            # Test 2: Knowledge graph
            print("\n  Test 6.2: Knowledge graph building...")
            graph = context_engine.build_knowledge_graph(context)
            assert 'nodes' in graph, "Should have nodes"
            assert 'connections' in graph, "Should have connections"
            print(
                f"    ✅ Graph: {len(graph['nodes'])} node categories, {len(graph['connections'])} connections")

            # Test 3: Intent prediction
            print("\n  Test 6.3: Intent prediction...")
            prediction = context_engine.predict_intent(
                "Optimize the system performance")
            assert 'primary_intent' in prediction, "Should predict intent"
            assert prediction['confidence'] > 0, "Should have confidence"
            print(
                f"    ✅ Intent: {prediction['primary_intent']}, Confidence: {prediction['confidence']*100:.0f}%")

            # Test 4: Strategic planning
            print("\n  Test 6.4: Quarterly plan generation...")
            strategist = AuroraStrategist()
            plan = strategist.generate_quarterly_plan()
            assert 'months' in plan, "Should have monthly breakdown"
            assert len(plan['months']) == 3, "Should have 3 months"
            print(
                f"    ✅ Plan: {plan['period']}, {len(plan['months'])} months")

            # Test 5: Resource optimization
            print("\n  Test 6.5: Resource allocation...")
            allocation = strategist.optimize_resource_allocation(plan)
            assert 'compute_resources' in allocation, "Should allocate compute"
            assert allocation['efficiency_score'] > 0, "Should have efficiency score"
            print(
                f"    ✅ Efficiency: {allocation['efficiency_score']*100:.0f}%")

            self.results.append({"phase": "Phase 6", "status": "PASS"})
            self.passed += 1
            print("\n✅ PHASE 6: ALL TESTS PASSED")
            return True

        except Exception as e:
            print(f"\n❌ PHASE 6 FAILED: {e}")
            self.results.append(
                {"phase": "Phase 6", "status": "FAIL", "error": str(e)})
            self.failed += 1
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("🌟 AURORA INTEGRATION TEST SUITE")
        print("="*60)
        print(f"Started: {datetime.now().isoformat()}")
        print(f"Testing all 6 phases of autonomous evolution")
        print("="*60)

        # Run all phase tests
        self.test_phase_1_self_monitoring()
        self.test_phase_2_tier_expansion()
        self.test_phase_3_tier_orchestration()
        self.test_phase_4_performance_optimization()
        self.test_phase_5_full_autonomy()
        self.test_phase_6_strategic_planning()

        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Phases Tested: {len(self.results)}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(
            f"Success Rate: {(self.passed / len(self.results) * 100) if self.results else 0:.0f}%")
        print("="*60)

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED - AURORA FULLY OPERATIONAL")
            return True
        else:
            print(f"\n⚠️  {self.failed} PHASE(S) FAILED - REVIEW REQUIRED")
            return False


def main():
    """Run integration tests"""
    tester = AuroraIntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
