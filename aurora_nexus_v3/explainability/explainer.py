"""
Explainable AI System
Self-contained transparent decision explanations with reasoning chains
No external APIs - uses decision tracing, reasoning visualization, and confidence explanation
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ExplanationLevel(Enum):
    """Explanation detail level"""

    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


@dataclass
class DecisionStep:
    """Decision step in reasoning chain"""

    step_number: int
    description: str
    reasoning: str
    confidence: float
    alternatives_considered: list[str] | None = None


@dataclass
class DecisionExplanation:
    """Decision explanation"""

    decision: str
    reasoning_chain: list[DecisionStep]
    confidence: float
    alternatives: list[dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)


class ExplainableAI:
    """
    Self-contained explainable AI system
    Transparent decision explanations with reasoning chains
    """

    def __init__(self):
        self.decision_history: list[DecisionExplanation] = []
        self.reasoning_traces: dict[str, list[DecisionStep]] = {}

    def explain_decision(
        self,
        decision: str,
        reasoning_chain: list[DecisionStep],
        alternatives: list[dict[str, Any]] | None = None,
    ) -> DecisionExplanation:
        """Generate explanation for a decision"""
        # Calculate overall confidence
        if reasoning_chain:
            avg_confidence = sum(step.confidence for step in reasoning_chain) / len(reasoning_chain)
        else:
            avg_confidence = 0.5

        explanation = DecisionExplanation(
            decision=decision,
            reasoning_chain=reasoning_chain,
            confidence=avg_confidence,
            alternatives=alternatives or [],
        )

        self.decision_history.append(explanation)
        return explanation

    def generate_reasoning_chain(
        self, problem: str, solution: str, steps: list[dict[str, Any]]
    ) -> list[DecisionStep]:
        """Generate reasoning chain from steps"""
        reasoning_chain: list[DecisionStep] = []

        for i, step_data in enumerate(steps, 1):
            step = DecisionStep(
                step_number=i,
                description=step_data.get("description", ""),
                reasoning=step_data.get("reasoning", ""),
                confidence=step_data.get("confidence", 0.5),
                alternatives_considered=step_data.get("alternatives"),
            )
            reasoning_chain.append(step)

        return reasoning_chain

    def visualize_reasoning(self, explanation: DecisionExplanation) -> dict[str, Any]:
        """Visualize reasoning chain"""
        visualization = {
            "decision": explanation.decision,
            "confidence": explanation.confidence,
            "steps": [],
            "alternatives": explanation.alternatives,
        }

        for step in explanation.reasoning_chain:
            visualization["steps"].append(
                {
                    "step": step.step_number,
                    "description": step.description,
                    "reasoning": step.reasoning,
                    "confidence": step.confidence,
                    "alternatives": step.alternatives_considered or [],
                }
            )

        return visualization

    def explain_confidence(self, explanation: DecisionExplanation) -> str:
        """Explain confidence level"""
        confidence = explanation.confidence

        if confidence >= 0.9:
            level = "very high"
            reason = "Strong evidence and clear reasoning support this decision"
        elif confidence >= 0.7:
            level = "high"
            reason = "Good evidence supports this decision with minor uncertainties"
        elif confidence >= 0.5:
            level = "moderate"
            reason = "Some evidence supports this decision, but alternatives exist"
        elif confidence >= 0.3:
            level = "low"
            reason = "Limited evidence, significant uncertainty"
        else:
            level = "very low"
            reason = "Weak evidence, high uncertainty, consider alternatives"

        return f"Confidence level: {level} ({confidence:.1%}). {reason}"

    def present_alternatives(self, explanation: DecisionExplanation) -> list[dict[str, Any]]:
        """Present alternative solutions"""
        alternatives = []

        for alt in explanation.alternatives:
            alternatives.append(
                {
                    "solution": alt.get("solution", ""),
                    "pros": alt.get("pros", []),
                    "cons": alt.get("cons", []),
                    "confidence": alt.get("confidence", 0.0),
                }
            )

        # Sort by confidence
        alternatives.sort(key=lambda x: x["confidence"], reverse=True)

        return alternatives

    def generate_explanation_summary(
        self, explanation: DecisionExplanation, level: ExplanationLevel = ExplanationLevel.SUMMARY
    ) -> str:
        """Generate explanation summary"""
        if level == ExplanationLevel.SUMMARY:
            return f"Decision: {explanation.decision}\nConfidence: {explanation.confidence:.1%}"

        elif level == ExplanationLevel.DETAILED:
            summary_parts = [
                f"Decision: {explanation.decision}",
                f"Confidence: {explanation.confidence:.1%}",
                "\nReasoning Steps:",
            ]

            for step in explanation.reasoning_chain[:5]:  # Top 5 steps
                summary_parts.append(f"{step.step_number}. {step.description}")

            return "\n".join(summary_parts)

        else:  # COMPREHENSIVE
            summary_parts = [
                f"Decision: {explanation.decision}",
                f"Confidence: {explanation.confidence:.1%}",
                "\nFull Reasoning Chain:",
            ]

            for step in explanation.reasoning_chain:
                summary_parts.append(
                    f"\nStep {step.step_number}: {step.description}\n"
                    f"Reasoning: {step.reasoning}\n"
                    f"Confidence: {step.confidence:.1%}"
                )

            if explanation.alternatives:
                summary_parts.append("\nAlternatives Considered:")
                for alt in explanation.alternatives:
                    summary_parts.append(f"- {alt.get('solution', 'Unknown')}")

            return "\n".join(summary_parts)

    def get_explanation_history(self) -> list[dict[str, Any]]:
        """Get explanation history"""
        return [
            {
                "decision": exp.decision,
                "confidence": exp.confidence,
                "steps_count": len(exp.reasoning_chain),
                "created_at": exp.created_at.isoformat(),
            }
            for exp in self.decision_history
        ]
