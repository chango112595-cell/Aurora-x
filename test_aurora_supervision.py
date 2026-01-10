"""
Aurora Supervision Test
Test Aurora's advanced systems with a complex task and monitor execution
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

# Import Aurora systems
try:
    from aurora_nexus_v3.analytics.advanced_analytics import AdvancedAnalytics
    from aurora_nexus_v3.core.advanced_reasoning_engine import AdvancedReasoningEngine
    from aurora_nexus_v3.core.config import NexusConfig
    from aurora_nexus_v3.core.creative_problem_solver import CreativeProblemSolver
    from aurora_nexus_v3.core.intelligent_task_decomposer import IntelligentTaskDecomposer
    from aurora_nexus_v3.core.universal_core import AuroraUniversalCore
    from aurora_nexus_v3.quality.code_intelligence import CodeQualityIntelligence
    from aurora_nexus_v3.security.advanced_analyzer import AdvancedSecurityAnalyzer

    AURORA_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Aurora systems not available: {e}")
    AURORA_AVAILABLE = False


class AuroraSupervisor:
    """Supervise Aurora's task execution"""

    def __init__(self):
        self.start_time = None
        self.events = []
        self.metrics = {}
        self.aurora_core = None

    def log_event(self, event_type: str, message: str, data: dict = None):
        """Log an event during supervision"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "data": data or {},
        }
        self.events.append(event)
        print(f"[{event['timestamp']}] [{event_type}] {message}")
        if data:
            print(f"  Data: {json.dumps(data, indent=2, default=str)}")

    async def initialize_aurora(self):
        """Initialize Aurora systems"""
        if not AURORA_AVAILABLE:
            self.log_event("ERROR", "Aurora systems not available")
            return False

        try:
            self.log_event("INIT", "Initializing Aurora Universal Core...")
            config = NexusConfig.from_env()
            self.aurora_core = AuroraUniversalCore(config=config)

            self.log_event("INIT", "Starting Aurora...")
            await self.aurora_core.start()

            self.log_event(
                "SUCCESS",
                "Aurora initialized successfully",
                {
                    "workers": self.aurora_core.WORKER_COUNT,
                    "tiers": self.aurora_core.TIER_COUNT,
                    "aems": self.aurora_core.AEM_COUNT,
                    "modules": self.aurora_core.MODULE_COUNT,
                },
            )

            return True
        except Exception as e:
            self.log_event("ERROR", f"Failed to initialize Aurora: {e}")
            return False

    async def assign_task(self, task_file: str):
        """Assign a task to Aurora"""
        self.start_time = time.time()

        try:
            # Load task
            task_path = Path(task_file)
            if not task_path.exists():
                self.log_event("ERROR", f"Task file not found: {task_file}")
                return None

            task_data = json.loads(task_path.read_text())
            self.log_event("TASK", "Task loaded", {"task_id": task_data.get("task_id")})

            # Decompose task
            self.log_event("PROCESS", "Decomposing task using Intelligent Task Decomposer...")
            decomposer = IntelligentTaskDecomposer()

            # Create Task object
            from aurora_nexus_v3.workers.worker import Task, TaskType

            task_obj = Task(
                id=task_data.get("task_id", "test_task"),
                task_type=TaskType.ANALYZE,
                payload={
                    "description": task_data["description"],
                    **task_data.get("requirements", {}),
                },
                priority=5,
                metadata=task_data.get("requirements", {}),
            )

            decomposition = decomposer.decompose_task(task=task_obj)
            subtasks = decomposition.subtasks

            self.log_event(
                "PROCESS",
                f"Task decomposed into {len(subtasks)} subtasks",
                {
                    "subtasks": [st.description for st in subtasks[:5]],  # First 5
                    "execution_order_groups": len(decomposition.execution_order),
                },
            )

            # Use advanced reasoning
            self.log_event("PROCESS", "Applying advanced reasoning...")
            reasoning_engine = AdvancedReasoningEngine()
            reasoning_result = reasoning_engine.chain_of_thought_reasoning(
                problem=task_data["description"],
                context={"requirements": task_data.get("requirements", {})},
            )

            # Handle ReasoningChain object
            reasoning_steps_count = (
                len(reasoning_result.reasoning_steps)
                if hasattr(reasoning_result, "reasoning_steps")
                else 0
            )
            conclusion = (
                reasoning_result.conclusion
                if hasattr(reasoning_result, "conclusion")
                else str(reasoning_result)[:100]
            )

            self.log_event(
                "REASONING",
                "Reasoning chain generated",
                {
                    "steps": reasoning_steps_count,
                    "conclusion": conclusion[:100]
                    if isinstance(conclusion, str)
                    else str(conclusion)[:100],
                },
            )

            # Use creative problem solving
            self.log_event("PROCESS", "Exploring creative solutions...")
            creative_solver = CreativeProblemSolver()
            try:
                creative_solutions = creative_solver.solve_creatively(
                    problem=task_data["description"], constraints=task_data.get("requirements", {})
                )

                # Handle Solution objects
                solutions_list = []
                for sol in creative_solutions[:5]:
                    if hasattr(sol, "description"):
                        solutions_list.append(
                            {
                                "description": sol.description[:100],
                                "novelty": getattr(sol, "novelty_score", 0),
                                "feasibility": getattr(sol, "feasibility_score", 0),
                            }
                        )
                    else:
                        solutions_list.append({"description": str(sol)[:100]})

                self.log_event(
                    "CREATIVE",
                    f"Generated {len(creative_solutions)} creative solutions",
                    {"solutions": solutions_list[:3]},
                )
            except Exception as e:
                self.log_event(
                    "WARN", f"Creative solving had issue: {e}", {"error_type": type(e).__name__}
                )
                creative_solutions = []

            # Execute security analysis
            self.log_event("PROCESS", "Running security analysis...")
            security_analyzer = AdvancedSecurityAnalyzer()

            # Sample code files for analysis
            sample_files = [
                "aurora_nexus_v3/core/universal_core.py",
                "aurora_nexus_v3/workers/worker.py",
                "server/rag-system.ts",
            ]

            security_issues = []
            for file_path in sample_files:
                file = Path(file_path)
                if file.exists():
                    code = file.read_text()
                    issues = security_analyzer.analyze_code(code, str(file_path))
                    security_issues.extend(issues)

            risk_assessment = security_analyzer.assess_risk(security_issues)

            self.log_event(
                "SECURITY",
                "Security analysis complete",
                {
                    "issues_found": len(security_issues),
                    "risk_level": risk_assessment.get("risk_level"),
                    "risk_score": risk_assessment.get("risk_score"),
                },
            )

            # Execute code quality analysis
            self.log_event("PROCESS", "Running code quality analysis...")
            quality_analyzer = CodeQualityIntelligence()

            quality_results = {}
            for file_path in sample_files:
                file = Path(file_path)
                if file.exists():
                    code = file.read_text()
                    quality = quality_analyzer.analyze_code_quality(code, str(file_path))
                    quality_results[file_path] = quality

            avg_quality = (
                sum(q.get("metrics", {}).get("quality_score", 0) for q in quality_results.values())
                / len(quality_results)
                if quality_results
                else 0
            )

            self.log_event(
                "QUALITY",
                "Code quality analysis complete",
                {
                    "files_analyzed": len(quality_results),
                    "average_quality_score": round(avg_quality, 2),
                },
            )

            # Record analytics
            self.log_event("PROCESS", "Recording analytics metrics...")
            analytics = AdvancedAnalytics()
            analytics.record_metric("task_execution_time", time.time() - self.start_time)
            analytics.record_metric("security_issues", len(security_issues))
            analytics.record_metric("code_quality_score", avg_quality)
            analytics.record_metric("subtasks_generated", len(subtasks))
            analytics.record_metric("creative_solutions", len(creative_solutions))

            insights = analytics.get_insights()

            self.log_event(
                "ANALYTICS",
                "Analytics recorded",
                {
                    "total_metrics": insights.get("total_metrics", 0),
                    "recommendations": len(insights.get("recommendations", [])),
                },
            )

            # Generate final report
            report = {
                "task_id": task_data.get("task_id"),
                "execution_time_seconds": round(time.time() - self.start_time, 2),
                "subtasks": [
                    {
                        "id": st.subtask_id,
                        "description": st.description,
                        "type": st.task_type.value,
                        "priority": st.priority,
                    }
                    for st in subtasks
                ],
                "reasoning": {
                    "steps_count": reasoning_steps_count,
                    "conclusion": conclusion[:200]
                    if isinstance(conclusion, str)
                    else str(conclusion)[:200],
                    "reasoning_steps": [
                        {
                            "step": i + 1,
                            "description": step.description
                            if hasattr(step, "description")
                            else str(step),
                        }
                        for i, step in enumerate(reasoning_result.reasoning_steps[:5])
                    ]
                    if hasattr(reasoning_result, "reasoning_steps")
                    else [],
                },
                "creative_solutions": [
                    {
                        "description": sol.description[:200]
                        if hasattr(sol, "description")
                        else str(sol)[:200],
                        "novelty": getattr(sol, "novelty_score", 0),
                        "feasibility": getattr(sol, "feasibility_score", 0),
                    }
                    for sol in creative_solutions[:5]
                ]
                if creative_solutions
                else [],
                "security_analysis": {
                    "issues": len(security_issues),
                    "risk_assessment": risk_assessment,
                    "top_issues": [
                        {
                            "type": issue.vulnerability_type.value,
                            "severity": issue.severity.value,
                            "location": issue.location,
                            "description": issue.description,
                        }
                        for issue in security_issues[:10]
                    ],
                },
                "code_quality": {
                    "files_analyzed": len(quality_results),
                    "average_score": round(avg_quality, 2),
                    "quality_by_file": {
                        k: v.get("metrics", {}).get("quality_level", "unknown")
                        for k, v in quality_results.items()
                    },
                },
                "analytics": insights,
                "systems_used": [
                    "IntelligentTaskDecomposer",
                    "AdvancedReasoningEngine",
                    "CreativeProblemSolver",
                    "AdvancedSecurityAnalyzer",
                    "CodeQualityIntelligence",
                    "AdvancedAnalytics",
                ],
            }

            self.log_event(
                "SUCCESS",
                "Task execution complete!",
                {
                    "execution_time": report["execution_time_seconds"],
                    "systems_used": len(report["systems_used"]),
                },
            )

            return report

        except Exception as e:
            self.log_event("ERROR", f"Task execution failed: {e}", {"error_type": type(e).__name__})
            import traceback

            self.log_event("ERROR", "Traceback", {"traceback": traceback.format_exc()})
            return None

    def generate_supervision_report(self, task_result: dict = None):
        """Generate supervision report"""
        report = {
            "supervision_session": {
                "start_time": self.start_time,
                "end_time": time.time(),
                "duration_seconds": round(time.time() - self.start_time, 2)
                if self.start_time
                else 0,
                "total_events": len(self.events),
            },
            "events": self.events,
            "task_result": task_result,
            "aurora_status": {
                "initialized": self.aurora_core is not None,
                "workers": self.aurora_core.WORKER_COUNT if self.aurora_core else 0,
                "systems_available": AURORA_AVAILABLE,
            },
        }

        return report


async def main():
    """Main supervision function"""
    print("=" * 80)
    print("AURORA SUPERVISION TEST")
    print("=" * 80)
    print()

    supervisor = AuroraSupervisor()

    # Initialize Aurora
    print("[SUPERVISOR] Initializing Aurora...")
    initialized = await supervisor.initialize_aurora()

    if not initialized:
        print("[SUPERVISOR] Aurora initialization failed. Continuing with limited functionality...")

    # Assign task
    print()
    print("[SUPERVISOR] Assigning complex task to Aurora...")
    print()

    task_result = await supervisor.assign_task("aurora_test_task.json")

    # Generate report
    print()
    print("[SUPERVISOR] Generating supervision report...")
    report = supervisor.generate_supervision_report(task_result)

    # Save report
    report_file = Path("aurora_supervision_report.json")
    report_file.write_text(json.dumps(report, indent=2, default=str))

    print()
    print("=" * 80)
    print("SUPERVISION REPORT SUMMARY")
    print("=" * 80)
    print(f"Total Events: {len(supervisor.events)}")
    print(f"Execution Time: {report['supervision_session']['duration_seconds']:.2f} seconds")
    print(f"Aurora Initialized: {report['aurora_status']['initialized']}")

    if task_result:
        print("\nTask Result:")
        print(f"  - Subtasks Generated: {len(task_result.get('subtasks', []))}")
        print(
            f"  - Security Issues Found: {task_result.get('security_analysis', {}).get('issues', 0)}"
        )
        print(
            f"  - Code Quality Score: {task_result.get('code_quality', {}).get('average_score', 0)}"
        )
        print(f"  - Systems Used: {len(task_result.get('systems_used', []))}")
        print(f"\nFull report saved to: {report_file}")
    else:
        print("\nTask execution failed - see events for details")

    print("=" * 80)

    return report


if __name__ == "__main__":
    asyncio.run(main())
