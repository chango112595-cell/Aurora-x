"""
Advanced Aurora Integration Module
Integrates all advanced capabilities into Aurora core
Self-contained - wires together reasoning, creativity, learning, prediction
"""

from typing import Any

# Import all advanced capabilities
try:
    from .advanced_reasoning_engine import AdvancedReasoningEngine
    from .continuous_learner import ContinuousLearner
    from .creative_problem_solver import CreativeProblemSolver
    from .intelligent_task_decomposer import IntelligentTaskDecomposer
    from .predictive_issue_detector import PredictiveIssueDetector

    ADVANCED_MODULES_AVAILABLE = True
except ImportError:
    ADVANCED_MODULES_AVAILABLE = False
    AdvancedReasoningEngine = None
    CreativeProblemSolver = None
    IntelligentTaskDecomposer = None
    PredictiveIssueDetector = None
    ContinuousLearner = None


class AdvancedAuroraIntegration:
    """
    Integrates all advanced capabilities into Aurora
    Makes everything work together seamlessly
    """

    def __init__(self, core: Any = None):
        self.core = core

        # Initialize all advanced modules
        if ADVANCED_MODULES_AVAILABLE:
            self.reasoning_engine = AdvancedReasoningEngine()
            self.creative_solver = CreativeProblemSolver()
            self.task_decomposer = IntelligentTaskDecomposer()
            self.predictive_detector = PredictiveIssueDetector()
            self.continuous_learner = ContinuousLearner()
        else:
            self.reasoning_engine = None
            self.creative_solver = None
            self.task_decomposer = None
            self.predictive_detector = None
            self.continuous_learner = None

    def process_task_advanced(self, task: Any, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Process a task using all advanced capabilities
        """
        context = context or {}

        if not ADVANCED_MODULES_AVAILABLE:
            return {"status": "advanced_modules_unavailable"}

        # Step 1: Decompose task if complex
        decomposition = None
        if self.task_decomposer:
            decomposition = self.task_decomposer.decompose_task(task, context)
            if len(decomposition.subtasks) > 1:
                # Complex task - use decomposition
                return {
                    "status": "decomposed",
                    "decomposition": {
                        "subtasks_count": len(decomposition.subtasks),
                        "execution_order": decomposition.execution_order,
                        "estimated_duration_ms": decomposition.total_estimated_duration_ms,
                    },
                }

        # Step 2: Use reasoning to understand task
        reasoning_result = None
        if self.reasoning_engine:
            problem_description = str(task.payload) if hasattr(task, "payload") else str(task)
            reasoning_chain = self.reasoning_engine.chain_of_thought_reasoning(
                problem_description, context
            )
            reasoning_result = {
                "steps": len(reasoning_chain.steps),
                "conclusion": reasoning_chain.final_conclusion,
                "confidence": reasoning_chain.confidence,
            }

        # Step 3: Generate creative solutions
        creative_solutions = None
        if self.creative_solver:
            problem = str(task.payload) if hasattr(task, "payload") else str(task)
            solutions = self.creative_solver.solve_creatively(problem, context=context)
            creative_solutions = [
                {
                    "description": s.description,
                    "novelty": s.novelty_score,
                    "feasibility": s.feasibility_score,
                    "technique": s.technique.value,
                }
                for s in solutions[:3]  # Top 3
            ]

        # Step 4: Check for predicted issues
        predictions = None
        if self.predictive_detector:
            predictions_list = self.predictive_detector.predict_issues()
            predictions = [
                {
                    "issue_type": p.issue_type,
                    "predicted_time": p.predicted_occurrence_time.isoformat(),
                    "confidence": p.confidence.value,
                    "severity": p.severity.value,
                }
                for p in predictions_list[:5]  # Top 5
            ]

        return {
            "status": "processed",
            "reasoning": reasoning_result,
            "creative_solutions": creative_solutions,
            "predictions": predictions,
            "advanced_capabilities_used": True,
        }

    def learn_from_experience(
        self,
        context: dict[str, Any],
        action: str,
        outcome: dict[str, Any],
        success: bool,
    ):
        """Learn from an experience"""
        if self.continuous_learner:
            self.continuous_learner.learn_from_experience(context, action, outcome, success)

    def get_advanced_status(self) -> dict[str, Any]:
        """Get status of all advanced capabilities"""
        status = {
            "advanced_modules_available": ADVANCED_MODULES_AVAILABLE,
        }

        if ADVANCED_MODULES_AVAILABLE:
            status.update(
                {
                    "reasoning_engine": self.reasoning_engine.get_status()
                    if self.reasoning_engine
                    else None,
                    "creative_solver": self.creative_solver.get_status()
                    if self.creative_solver
                    else None,
                    "task_decomposer": self.task_decomposer.get_status()
                    if self.task_decomposer
                    else None,
                    "predictive_detector": self.predictive_detector.get_status()
                    if self.predictive_detector
                    else None,
                    "continuous_learner": self.continuous_learner.get_learning_stats()
                    if self.continuous_learner
                    else None,
                }
            )

        return status
