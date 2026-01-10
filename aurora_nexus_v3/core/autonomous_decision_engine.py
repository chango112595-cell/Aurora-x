"""
Autonomous Decision-Making Engine
Self-contained decision-making with multi-criteria analysis and risk assessment
No external APIs - uses decision trees, utility functions, and game theory
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .advanced_reasoning_engine import AdvancedReasoningEngine


class DecisionType(Enum):
    """Types of decisions"""

    STRATEGIC = "strategic"  # Long-term, high-impact
    TACTICAL = "tactical"  # Medium-term, medium-impact
    OPERATIONAL = "operational"  # Short-term, low-impact
    CRITICAL = "critical"  # Immediate, high-impact


class RiskLevel(Enum):
    """Risk levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DecisionOption:
    """A decision option"""

    option_id: str
    description: str
    expected_utility: float
    risk_level: RiskLevel
    confidence: float
    criteria_scores: dict[str, float] = field(default_factory=dict)
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)


@dataclass
class Decision:
    """A decision made by Aurora"""

    decision_id: str
    decision_type: DecisionType
    context: dict[str, Any]
    options: list[DecisionOption]
    selected_option: DecisionOption | None
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0


class AutonomousDecisionEngine:
    """
    Self-contained autonomous decision-making engine
    Makes decisions using multi-criteria analysis, risk assessment, and utility maximization
    """

    def __init__(self):
        self.decision_history: list[Decision] = []
        self.reasoning_engine = AdvancedReasoningEngine()
        self.decision_patterns: dict[str, list[dict[str, Any]]] = {}
        self.criteria_weights: dict[
            str, dict[str, float]
        ] = {}  # decision_type -> {criterion: weight}
        self._initialize_criteria_weights()

    def _initialize_criteria_weights(self):
        """Initialize criteria weights for different decision types"""
        self.criteria_weights = {
            DecisionType.STRATEGIC.value: {
                "long_term_value": 0.4,
                "risk": 0.3,
                "feasibility": 0.2,
                "resource_requirement": 0.1,
            },
            DecisionType.TACTICAL.value: {
                "immediate_value": 0.3,
                "risk": 0.25,
                "feasibility": 0.25,
                "resource_requirement": 0.2,
            },
            DecisionType.OPERATIONAL.value: {
                "efficiency": 0.4,
                "risk": 0.2,
                "feasibility": 0.3,
                "resource_requirement": 0.1,
            },
            DecisionType.CRITICAL.value: {
                "speed": 0.4,
                "risk": 0.3,
                "effectiveness": 0.2,
                "resource_requirement": 0.1,
            },
        }

    def make_decision(
        self,
        decision_type: DecisionType,
        context: dict[str, Any],
        options: list[str] | None = None,
    ) -> Decision:
        """
        Make an autonomous decision
        """
        # Generate options if not provided
        if not options:
            options = self._generate_options(context, decision_type)

        # Evaluate each option
        evaluated_options = []
        for option_desc in options:
            option = self._evaluate_option(option_desc, context, decision_type)
            evaluated_options.append(option)

        # Select best option using multi-criteria decision analysis
        selected_option = self._select_best_option(evaluated_options, decision_type)

        # Generate reasoning
        reasoning = self._generate_reasoning(evaluated_options, selected_option, context)

        # Create decision
        decision = Decision(
            decision_id=str(uuid.uuid4()),
            decision_type=decision_type,
            context=context,
            options=evaluated_options,
            selected_option=selected_option,
            reasoning=reasoning,
            confidence=selected_option.confidence if selected_option else 0.0,
        )

        self.decision_history.append(decision)

        # Keep only recent decisions (last 1000)
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]

        return decision

    def _generate_options(self, context: dict[str, Any], decision_type: DecisionType) -> list[str]:
        """Generate decision options"""
        options = []

        # Use reasoning engine to generate options
        problem = context.get("problem", str(context))
        reasoning_chain = self.reasoning_engine.chain_of_thought_reasoning(
            f"Generate options for: {problem}", context
        )

        # Extract options from reasoning steps
        for step in reasoning_chain.steps:
            if "option" in step.conclusion.lower() or "approach" in step.conclusion.lower():
                options.append(step.conclusion)

        # If no options found, generate default options
        if not options:
            options = [
                f"Option 1: Proceed with {problem}",
                f"Option 2: Delay {problem}",
                f"Option 3: Modify approach to {problem}",
            ]

        return options[:5]  # Limit to 5 options

    def _evaluate_option(
        self,
        option_desc: str,
        context: dict[str, Any],
        decision_type: DecisionType,
    ) -> DecisionOption:
        """Evaluate a decision option"""
        # Get criteria weights for decision type
        weights = self.criteria_weights.get(decision_type.value, {})

        # Score each criterion
        criteria_scores = {}
        for criterion, _weight in weights.items():
            score = self._score_criterion(criterion, option_desc, context)
            criteria_scores[criterion] = score

        # Calculate expected utility
        expected_utility = sum(
            score * weights.get(criterion, 0.0) for criterion, score in criteria_scores.items()
        )

        # Assess risk
        risk_level = self._assess_risk(option_desc, context)

        # Calculate confidence
        confidence = self._calculate_confidence(criteria_scores, context)

        # Identify pros and cons
        pros = self._identify_pros(option_desc, context)
        cons = self._identify_cons(option_desc, context)

        return DecisionOption(
            option_id=str(uuid.uuid4()),
            description=option_desc,
            expected_utility=expected_utility,
            risk_level=risk_level,
            confidence=confidence,
            criteria_scores=criteria_scores,
            pros=pros,
            cons=cons,
        )

    def _score_criterion(self, criterion: str, option_desc: str, context: dict[str, Any]) -> float:
        """Score a criterion for an option"""
        option_lower = option_desc.lower()

        # Criterion-specific scoring
        if criterion == "long_term_value":
            if any(word in option_lower for word in ["improve", "enhance", "optimize", "upgrade"]):
                return 0.8
            return 0.5

        elif criterion == "immediate_value":
            if any(word in option_lower for word in ["quick", "fast", "immediate", "now"]):
                return 0.8
            return 0.5

        elif criterion == "efficiency":
            if any(word in option_lower for word in ["efficient", "optimize", "streamline"]):
                return 0.8
            return 0.5

        elif criterion == "speed":
            if any(word in option_lower for word in ["fast", "quick", "rapid", "immediate"]):
                return 0.9
            return 0.4

        elif criterion == "risk":
            # Lower risk is better, so invert score
            risk_indicators = ["dangerous", "risky", "uncertain", "experimental"]
            if any(word in option_lower for word in risk_indicators):
                return 0.3  # High risk = low score
            return 0.7  # Low risk = high score

        elif criterion == "feasibility":
            if any(
                word in option_lower for word in ["simple", "easy", "straightforward", "proven"]
            ):
                return 0.8
            return 0.5

        elif criterion == "resource_requirement":
            # Lower resource requirement is better
            resource_indicators = ["expensive", "resource", "complex", "requires"]
            if any(word in option_lower for word in resource_indicators):
                return 0.4  # High requirement = low score
            return 0.7  # Low requirement = high score

        elif criterion == "effectiveness":
            if any(
                word in option_lower for word in ["effective", "successful", "proven", "reliable"]
            ):
                return 0.8
            return 0.5

        return 0.5  # Default score

    def _assess_risk(self, option_desc: str, context: dict[str, Any]) -> RiskLevel:
        """Assess risk level of an option"""
        option_lower = option_desc.lower()

        # High risk indicators
        if any(word in option_lower for word in ["experimental", "untested", "dangerous", "risky"]):
            return RiskLevel.HIGH

        # Critical risk indicators
        critical_words = ["critical", "system", "production", "data"]
        if (
            any(word in option_lower for word in critical_words)
            and "backup" not in option_lower
            and "safe" not in option_lower
        ):
            return RiskLevel.CRITICAL

        # Medium risk indicators
        if any(word in option_lower for word in ["modify", "change", "update"]):
            return RiskLevel.MEDIUM

        return RiskLevel.LOW

    def _calculate_confidence(
        self,
        criteria_scores: dict[str, float],
        context: dict[str, Any],
    ) -> float:
        """Calculate confidence in evaluation"""
        # Average of criteria scores
        avg_score = sum(criteria_scores.values()) / len(criteria_scores) if criteria_scores else 0.5

        # Boost confidence if context is clear
        context_clarity = 1.0 if len(str(context)) > 50 else 0.7

        return min(avg_score * context_clarity, 1.0)

    def _identify_pros(self, option_desc: str, context: dict[str, Any]) -> list[str]:
        """Identify pros of an option"""
        pros = []
        option_lower = option_desc.lower()

        if "fast" in option_lower or "quick" in option_lower:
            pros.append("Fast execution")
        if "simple" in option_lower or "easy" in option_lower:
            pros.append("Simple implementation")
        if "proven" in option_lower or "reliable" in option_lower:
            pros.append("Proven approach")
        if "efficient" in option_lower:
            pros.append("Efficient resource usage")

        return pros[:3]  # Limit to 3

    def _identify_cons(self, option_desc: str, context: dict[str, Any]) -> list[str]:
        """Identify cons of an option"""
        cons = []
        option_lower = option_desc.lower()

        if "experimental" in option_lower:
            cons.append("Untested approach")
        if "expensive" in option_lower or "resource" in option_lower:
            cons.append("High resource requirement")
        if "complex" in option_lower:
            cons.append("Complex implementation")
        if "risky" in option_lower:
            cons.append("Higher risk")

        return cons[:3]  # Limit to 3

    def _select_best_option(
        self,
        options: list[DecisionOption],
        decision_type: DecisionType,
    ) -> DecisionOption | None:
        """Select best option using multi-criteria analysis"""
        if not options:
            return None

        # Sort by expected utility (descending)
        sorted_options = sorted(options, key=lambda o: o.expected_utility, reverse=True)

        # For critical decisions, prefer lower risk
        if decision_type == DecisionType.CRITICAL:
            # Filter by risk level
            low_risk_options = [o for o in sorted_options if o.risk_level == RiskLevel.LOW]
            if low_risk_options:
                return low_risk_options[0]

        # Return highest utility option
        return sorted_options[0]

    def _generate_reasoning(
        self,
        options: list[DecisionOption],
        selected_option: DecisionOption | None,
        context: dict[str, Any],
    ) -> str:
        """Generate reasoning for decision"""
        if not selected_option:
            return "No suitable option found"

        reasoning_parts = [
            f"Selected option: {selected_option.description}",
            f"Expected utility: {selected_option.expected_utility:.2f}",
            f"Risk level: {selected_option.risk_level.value}",
            f"Confidence: {selected_option.confidence:.2f}",
        ]

        if selected_option.pros:
            reasoning_parts.append(f"Pros: {', '.join(selected_option.pros)}")
        if selected_option.cons:
            reasoning_parts.append(f"Cons: {', '.join(selected_option.cons)}")

        return ". ".join(reasoning_parts)

    def get_decision_history(self) -> list[Decision]:
        """Get decision history"""
        return self.decision_history

    def get_status(self) -> dict[str, Any]:
        """Get engine status"""
        return {
            "total_decisions": len(self.decision_history),
            "decision_types": list(set(d.decision_type.value for d in self.decision_history)),
            "average_confidence": (
                sum(d.confidence for d in self.decision_history) / len(self.decision_history)
                if self.decision_history
                else 0.0
            ),
        }
