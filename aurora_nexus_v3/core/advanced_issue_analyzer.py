"""
Advanced Issue Analysis System
Self-contained deep issue analysis with root cause analysis and impact assessment
No external APIs - uses causal analysis, pattern matching, and impact graphs
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..workers.issue_detector import DetectedIssue, IssueSeverity
from .advanced_reasoning_engine import AdvancedReasoningEngine
from .predictive_issue_detector import PredictiveIssueDetector


class AnalysisDepth(Enum):
    """Analysis depth levels"""

    SURFACE = "surface"  # Quick analysis
    STANDARD = "standard"  # Standard analysis
    DEEP = "deep"  # Deep root cause analysis
    COMPREHENSIVE = "comprehensive"  # Full comprehensive analysis


@dataclass
class IssueAnalysis:
    """Comprehensive issue analysis"""

    analysis_id: str
    issue: DetectedIssue
    root_causes: list[str]
    contributing_factors: list[str]
    impact_assessment: dict[str, Any]
    affected_components: list[str]
    severity_justification: str
    recommended_actions: list[str]
    analysis_depth: AnalysisDepth
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class AdvancedIssueAnalyzer:
    """
    Self-contained advanced issue analysis system
    Performs deep analysis of issues with root cause analysis
    """

    def __init__(self):
        self.reasoning_engine = AdvancedReasoningEngine()
        self.predictive_detector = PredictiveIssueDetector()
        self.analysis_history: list[IssueAnalysis] = []
        self.issue_patterns: dict[str, list[dict[str, Any]]] = {}
        self.root_cause_library: dict[str, list[str]] = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize analysis patterns"""
        self.root_cause_library = {
            "import_error": [
                "Missing dependency",
                "Incorrect import path",
                "Circular import",
                "Module not installed",
            ],
            "syntax_error": [
                "Invalid syntax",
                "Missing bracket/parenthesis",
                "Indentation error",
                "Type mismatch",
            ],
            "runtime_error": [
                "Null pointer exception",
                "Index out of bounds",
                "Type error",
                "Resource not available",
            ],
            "performance": [
                "Inefficient algorithm",
                "Memory leak",
                "CPU bottleneck",
                "I/O bottleneck",
            ],
        }

    def analyze_issue(
        self,
        issue: DetectedIssue,
        depth: AnalysisDepth = AnalysisDepth.STANDARD,
    ) -> IssueAnalysis:
        """
        Perform comprehensive issue analysis
        """
        analysis_id = str(uuid.uuid4())

        # Step 1: Root cause analysis
        root_causes = self._analyze_root_causes(issue, depth)

        # Step 2: Contributing factors
        contributing_factors = self._identify_contributing_factors(issue, root_causes)

        # Step 3: Impact assessment
        impact_assessment = self._assess_impact(issue, root_causes)

        # Step 4: Affected components
        affected_components = self._identify_affected_components(issue, impact_assessment)

        # Step 5: Severity justification
        severity_justification = self._justify_severity(issue, impact_assessment)

        # Step 6: Recommended actions
        recommended_actions = self._recommend_actions(issue, root_causes, impact_assessment)

        # Step 7: Calculate confidence
        confidence = self._calculate_confidence(root_causes, impact_assessment)

        # Create analysis
        analysis = IssueAnalysis(
            analysis_id=analysis_id,
            issue=issue,
            root_causes=root_causes,
            contributing_factors=contributing_factors,
            impact_assessment=impact_assessment,
            affected_components=affected_components,
            severity_justification=severity_justification,
            recommended_actions=recommended_actions,
            analysis_depth=depth,
            confidence=confidence,
        )

        self.analysis_history.append(analysis)

        # Keep only recent analyses (last 5000)
        if len(self.analysis_history) > 5000:
            self.analysis_history = self.analysis_history[-5000:]

        return analysis

    def _analyze_root_causes(
        self,
        issue: DetectedIssue,
        depth: AnalysisDepth,
    ) -> list[str]:
        """Analyze root causes"""
        root_causes = []

        # Use reasoning engine for causal inference
        causal_analysis = self.reasoning_engine.causal_inference(
            f"Issue: {issue.type} - {issue.description}",
            {"target": issue.target, "category": issue.category.value},
        )

        # Extract potential causes
        potential_causes = causal_analysis.get("potential_causes", [])
        root_causes.extend([c["cause"] for c in potential_causes[:3]])

        # Use pattern library
        issue_type_lower = issue.type.lower()
        for pattern_type, causes in self.root_cause_library.items():
            if pattern_type in issue_type_lower:
                root_causes.extend(causes[:2])  # Top 2 from library
                break

        # Deep analysis if requested
        if depth in [AnalysisDepth.DEEP, AnalysisDepth.COMPREHENSIVE]:
            # Use chain-of-thought reasoning
            reasoning_chain = self.reasoning_engine.chain_of_thought_reasoning(
                f"Deep root cause analysis of {issue.type}",
                {"issue": issue.description, "target": issue.target},
            )

            # Extract insights from reasoning
            for step in reasoning_chain.steps:
                if "cause" in step.conclusion.lower() or "root" in step.conclusion.lower():
                    root_causes.append(step.conclusion)

        return list(set(root_causes))[:5]  # Top 5 unique causes

    def _identify_contributing_factors(
        self,
        issue: DetectedIssue,
        root_causes: list[str],
    ) -> list[str]:
        """Identify contributing factors"""
        factors = []

        # Extract from issue metadata
        if issue.metadata:
            factors.extend(
                [
                    f"{key}: {value}"
                    for key, value in issue.metadata.items()
                    if key not in ["timestamp", "worker_id"]
                ]
            )

        # Analyze context
        context_str = str(issue.target).lower()
        if "recent" in context_str or "change" in context_str:
            factors.append("Recent changes may have introduced issue")
        if "dependency" in context_str:
            factors.append("Dependency-related issue")

        return factors[:5]  # Top 5

    def _assess_impact(
        self,
        issue: DetectedIssue,
        root_causes: list[str],
    ) -> dict[str, Any]:
        """Assess impact of issue"""
        impact = {
            "severity": issue.severity.value,
            "affected_users": 0,
            "system_components": [],
            "data_risk": "low",
            "availability_impact": "none",
            "performance_impact": "none",
        }

        # Assess based on severity
        if issue.severity == IssueSeverity.CRITICAL:
            impact["affected_users"] = 100
            impact["data_risk"] = "high"
            impact["availability_impact"] = "critical"
            impact["performance_impact"] = "severe"
        elif issue.severity == IssueSeverity.HIGH:
            impact["affected_users"] = 50
            impact["data_risk"] = "medium"
            impact["availability_impact"] = "moderate"
            impact["performance_impact"] = "moderate"
        elif issue.severity == IssueSeverity.MEDIUM:
            impact["affected_users"] = 10
            impact["data_risk"] = "low"
            impact["availability_impact"] = "minimal"
            impact["performance_impact"] = "minimal"

        # Identify affected components
        target_lower = issue.target.lower()
        if "database" in target_lower:
            impact["system_components"].append("database")
        if "api" in target_lower or "endpoint" in target_lower:
            impact["system_components"].append("api")
        if "worker" in target_lower:
            impact["system_components"].append("workers")

        return impact

    def _identify_affected_components(
        self,
        issue: DetectedIssue,
        impact_assessment: dict[str, Any],
    ) -> list[str]:
        """Identify affected components"""
        components = impact_assessment.get("system_components", [])

        # Add components from target
        target_lower = issue.target.lower()
        if "core" in target_lower:
            components.append("core_system")
        if "memory" in target_lower:
            components.append("memory_system")
        if "task" in target_lower:
            components.append("task_system")

        return list(set(components))

    def _justify_severity(
        self,
        issue: DetectedIssue,
        impact_assessment: dict[str, Any],
    ) -> str:
        """Justify severity level"""
        severity = issue.severity.value
        impact = impact_assessment

        justification = (
            f"Issue classified as {severity} severity because: "
            f"Affects {impact['affected_users']} users, "
            f"Data risk: {impact['data_risk']}, "
            f"Availability impact: {impact['availability_impact']}, "
            f"Performance impact: {impact['performance_impact']}"
        )

        return justification

    def _recommend_actions(
        self,
        issue: DetectedIssue,
        root_causes: list[str],
        impact_assessment: dict[str, Any],
    ) -> list[str]:
        """Recommend actions to resolve issue"""
        actions = []

        # Immediate actions based on severity
        if issue.severity == IssueSeverity.CRITICAL:
            actions.append("Immediate isolation of affected component")
            actions.append("Emergency rollback if applicable")
            actions.append("Notify stakeholders immediately")

        # Actions based on root causes
        for cause in root_causes[:3]:
            if "missing" in cause.lower():
                actions.append(f"Install missing dependency: {cause}")
            elif "error" in cause.lower():
                actions.append(f"Fix error condition: {cause}")
            elif "performance" in cause.lower():
                actions.append(f"Optimize performance: {cause}")

        # Standard actions
        actions.append(f"Fix root cause: {root_causes[0] if root_causes else 'Unknown'}")
        actions.append("Add monitoring to prevent recurrence")
        actions.append("Update documentation")

        return actions[:10]  # Top 10

    def _calculate_confidence(
        self,
        root_causes: list[str],
        impact_assessment: dict[str, Any],
    ) -> float:
        """Calculate confidence in analysis"""
        confidence = 0.5  # Base confidence

        # More root causes = higher confidence
        if len(root_causes) > 0:
            confidence += 0.2
        if len(root_causes) > 2:
            confidence += 0.1

        # Impact assessment completeness
        if impact_assessment.get("system_components"):
            confidence += 0.1
        if impact_assessment.get("affected_users", 0) > 0:
            confidence += 0.1

        return min(confidence, 1.0)

    def get_analysis_history(self) -> list[IssueAnalysis]:
        """Get analysis history"""
        return self.analysis_history

    def get_analysis_stats(self) -> dict[str, Any]:
        """Get analysis statistics"""
        return {
            "total_analyses": len(self.analysis_history),
            "analyses_by_depth": {
                depth.value: len([a for a in self.analysis_history if a.analysis_depth == depth])
                for depth in AnalysisDepth
            },
            "average_confidence": (
                sum(a.confidence for a in self.analysis_history) / len(self.analysis_history)
                if self.analysis_history
                else 0.0
            ),
        }
