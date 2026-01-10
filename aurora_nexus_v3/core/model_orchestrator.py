"""
Multi-Model Integration System
Self-contained multi-strategy system for different task types
No external APIs - uses internal strategy selection and ensemble methods
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TaskType(Enum):
    """Task types"""

    REASONING = "reasoning"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    SYNTHESIS = "synthesis"
    DECISION = "decision"


class StrategyType(Enum):
    """Strategy types"""

    REASONING_ENGINE = "reasoning_engine"
    CREATIVE_SOLVER = "creative_solver"
    ANALYTICAL_ENGINE = "analytical_engine"
    OPTIMIZER = "optimizer"
    SYNTHESIZER = "synthesizer"
    DECISION_ENGINE = "decision_engine"


@dataclass
class StrategyResult:
    """Strategy execution result"""

    strategy: StrategyType
    result: Any
    confidence: float
    execution_time: float


class ModelOrchestrator:
    """
    Self-contained model orchestrator
    Selects and orchestrates different strategies for different tasks
    """

    def __init__(self):
        self.strategy_registry: dict[TaskType, list[StrategyType]] = {
            TaskType.REASONING: [StrategyType.REASONING_ENGINE, StrategyType.ANALYTICAL_ENGINE],
            TaskType.CREATIVE: [StrategyType.CREATIVE_SOLVER, StrategyType.SYNTHESIZER],
            TaskType.ANALYSIS: [StrategyType.ANALYTICAL_ENGINE, StrategyType.REASONING_ENGINE],
            TaskType.OPTIMIZATION: [StrategyType.OPTIMIZER, StrategyType.ANALYTICAL_ENGINE],
            TaskType.SYNTHESIS: [StrategyType.SYNTHESIZER, StrategyType.CREATIVE_SOLVER],
            TaskType.DECISION: [StrategyType.DECISION_ENGINE, StrategyType.REASONING_ENGINE],
        }

        self.strategy_performance: dict[StrategyType, dict[str, Any]] = {}

    def select_strategy(
        self, task_type: TaskType, context: dict[str, Any] | None = None
    ) -> StrategyType:
        """Select best strategy for task"""
        available_strategies = self.strategy_registry.get(task_type, [])

        if not available_strategies:
            # Default strategy
            return StrategyType.REASONING_ENGINE

        # Select based on performance history
        best_strategy = available_strategies[0]
        best_score = 0.0

        for strategy in available_strategies:
            perf = self.strategy_performance.get(strategy, {})
            score = perf.get("success_rate", 0.5) * perf.get("avg_confidence", 0.5)

            if score > best_score:
                best_score = score
                best_strategy = strategy

        return best_strategy

    def execute_with_strategy(
        self, task_type: TaskType, task: dict[str, Any], context: dict[str, Any] | None = None
    ) -> StrategyResult:
        """Execute task with selected strategy"""
        strategy = self.select_strategy(task_type, context)

        # Execute strategy (simplified - would call actual strategy implementations)
        result = self._execute_strategy(strategy, task)

        # Record performance
        self._record_performance(strategy, result)

        return result

    def _execute_strategy(self, strategy: StrategyType, task: dict[str, Any]) -> StrategyResult:
        """Execute a strategy using real implementations"""
        import time

        start_time = time.time()
        result_value = None
        confidence = 0.5

        # Execute actual strategy based on type
        try:
            if strategy == StrategyType.REASONING_ENGINE:
                # Use Advanced Reasoning Engine
                from .advanced_reasoning_engine import AdvancedReasoningEngine

                engine = AdvancedReasoningEngine()
                reasoning_result = engine.chain_of_thought_reasoning(
                    task.get("query", ""), context=task.get("context", {})
                )
                result_value = {
                    "reasoning_steps": len(reasoning_result.reasoning_steps),
                    "conclusion": reasoning_result.conclusion,
                    "confidence": reasoning_result.confidence,
                }
                confidence = reasoning_result.confidence

            elif strategy == StrategyType.CREATIVE_SOLVER:
                # Use Creative Problem Solver
                from .creative_problem_solver import CreativeProblemSolver

                solver = CreativeProblemSolver()
                solution = solver.solve_creatively(
                    problem=task.get("problem", ""), constraints=task.get("constraints", [])
                )
                result_value = {
                    "solution": solution.description,
                    "novelty": solution.novelty_score,
                    "feasibility": solution.feasibility_score,
                }
                confidence = solution.combined_score

            elif strategy == StrategyType.DECISION_ENGINE:
                # Use Autonomous Decision Engine
                from .autonomous_decision_engine import AutonomousDecisionEngine

                engine = AutonomousDecisionEngine()
                decision = engine.make_decision(
                    context=task.get("context", {}), options=task.get("options", [])
                )
                result_value = {
                    "decision": decision.choice,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                }
                confidence = decision.confidence

            elif strategy == StrategyType.ANALYTICAL_ENGINE:
                # Use Advanced Issue Analyzer
                from .advanced_issue_analyzer import AdvancedIssueAnalyzer

                analyzer = AdvancedIssueAnalyzer()
                from ..workers.issue_detector import DetectedIssue, IssueCategory, IssueSeverity

                issue = DetectedIssue(
                    id="analysis",
                    category=IssueCategory.SYSTEM,
                    severity=IssueSeverity.MEDIUM,
                    type="analysis",
                    target=task.get("target", ""),
                    description=task.get("description", ""),
                )
                analysis = analyzer.analyze_issue(issue)
                result_value = {
                    "root_causes": analysis.root_causes,
                    "impact": analysis.impact_level.value,
                    "confidence": analysis.confidence,
                }
                confidence = analysis.confidence

            elif strategy == StrategyType.OPTIMIZER:
                # Use Resource Optimizer
                from .resource_optimizer import ResourceOptimizer, ResourceType

                optimizer = ResourceOptimizer()
                optimization = optimizer.optimize_resources(
                    resource_type=ResourceType.CPU,
                    current_usage=task.get("current_usage", {}),
                    target_usage=task.get("target_usage", {}),
                )
                result_value = {
                    "optimization": optimization.recommendations,
                    "efficiency_gain": optimization.efficiency_gain,
                }
                confidence = 0.85

            elif strategy == StrategyType.SYNTHESIZER:
                # Use Intelligent Task Decomposer for synthesis
                from ..workers.worker import Task, TaskType
                from .intelligent_task_decomposer import IntelligentTaskDecomposer

                decomposer = IntelligentTaskDecomposer()
                task_obj = Task(id="synthesis", task_type=TaskType.CODE, payload=task)
                decomposition = decomposer.decompose_task(task_obj)
                result_value = {
                    "subtasks": len(decomposition.subtasks),
                    "execution_order": decomposition.execution_order,
                    "estimated_time": decomposition.estimated_time,
                }
                confidence = 0.8

            else:
                # Default fallback
                result_value = {"strategy": strategy.value, "task": task, "status": "executed"}
                confidence = 0.7

        except Exception as e:
            # Fallback on error
            result_value = {
                "strategy": strategy.value,
                "task": task,
                "error": str(e),
                "status": "error",
            }
            confidence = 0.3

        execution_time = time.time() - start_time

        return StrategyResult(
            strategy=strategy,
            result=result_value,
            confidence=confidence,
            execution_time=execution_time,
        )

    def ensemble_execute(
        self,
        task_type: TaskType,
        task: dict[str, Any],
        strategies: list[StrategyType] | None = None,
    ) -> dict[str, Any]:
        """Execute with multiple strategies and combine results"""
        if strategies is None:
            strategies = self.strategy_registry.get(task_type, [])[:3]  # Top 3

        results: list[StrategyResult] = []

        for strategy in strategies:
            result = self._execute_strategy(strategy, task)
            results.append(result)

        # Combine results
        combined_result = self._combine_results(results)

        return {
            "results": [
                {
                    "strategy": r.strategy.value,
                    "confidence": r.confidence,
                    "result": r.result,
                }
                for r in results
            ],
            "combined_result": combined_result,
            "consensus": self._calculate_consensus(results),
        }

    def _combine_results(self, results: list[StrategyResult]) -> Any:
        """Combine multiple strategy results"""
        if not results:
            return None

        # Weighted combination based on confidence
        total_weight = sum(r.confidence for r in results)

        if total_weight == 0:
            return results[0].result

        # Simple combination - return highest confidence result
        best_result = max(results, key=lambda r: r.confidence)
        return best_result.result

    def _calculate_consensus(self, results: list[StrategyResult]) -> float:
        """Calculate consensus between results"""
        if len(results) < 2:
            return 1.0

        # Simplified consensus calculation
        avg_confidence = sum(r.confidence for r in results) / len(results)
        return avg_confidence

    def _record_performance(self, strategy: StrategyType, result: StrategyResult):
        """Record strategy performance"""
        if strategy not in self.strategy_performance:
            self.strategy_performance[strategy] = {
                "execution_count": 0,
                "success_count": 0,
                "total_confidence": 0.0,
                "total_time": 0.0,
            }

        perf = self.strategy_performance[strategy]
        perf["execution_count"] += 1
        perf["total_confidence"] += result.confidence
        perf["total_time"] += result.execution_time

        if result.confidence > 0.7:
            perf["success_count"] += 1

        # Calculate derived metrics
        perf["success_rate"] = perf["success_count"] / perf["execution_count"]
        perf["avg_confidence"] = perf["total_confidence"] / perf["execution_count"]
        perf["avg_time"] = perf["total_time"] / perf["execution_count"]

    def get_strategy_stats(self) -> dict[str, Any]:
        """Get strategy statistics"""
        return {
            "strategies": {
                strategy.value: {
                    "executions": perf.get("execution_count", 0),
                    "success_rate": perf.get("success_rate", 0.0),
                    "avg_confidence": perf.get("avg_confidence", 0.0),
                    "avg_time": perf.get("avg_time", 0.0),
                }
                for strategy, perf in self.strategy_performance.items()
            }
        }
