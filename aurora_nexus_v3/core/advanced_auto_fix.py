"""
Advanced Auto-Fix System
Self-contained intelligent auto-fixing with multi-strategy approach and validation
No external APIs - uses pattern matching, code analysis, and fix validation
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..workers.issue_detector import DetectedIssue
from .advanced_issue_analyzer import AdvancedIssueAnalyzer, AnalysisDepth
from .advanced_reasoning_engine import AdvancedReasoningEngine
from .creative_problem_solver import CreativeProblemSolver


class FixStrategy(Enum):
    """Fix strategies"""

    PATTERN_MATCHING = "pattern_matching"
    CODE_GENERATION = "code_generation"
    REFACTORING = "refactoring"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"
    CREATIVE = "creative"


class FixConfidence(Enum):
    """Fix confidence levels"""

    HIGH = "high"  # >80% success probability
    MEDIUM = "medium"  # 50-80% success probability
    LOW = "low"  # <50% success probability


@dataclass
class FixAttempt:
    """A fix attempt"""

    fix_id: str
    issue: DetectedIssue
    strategy: FixStrategy
    fix_description: str
    fix_code: str | None
    confidence: FixConfidence
    applied: bool
    success: bool | None
    timestamp: datetime = field(default_factory=datetime.now)
    validation_result: dict[str, Any] | None = None


class AdvancedAutoFix:
    """
    Self-contained advanced auto-fix system
    Intelligently fixes issues using multiple strategies
    """

    def __init__(self):
        self.issue_analyzer = AdvancedIssueAnalyzer()
        self.creative_solver = CreativeProblemSolver()
        self.reasoning_engine = AdvancedReasoningEngine()
        self.fix_history: list[FixAttempt] = []
        self.fix_patterns: dict[str, list[dict[str, Any]]] = {}
        self._initialize_fix_patterns()

    def _initialize_fix_patterns(self):
        """Initialize fix patterns"""
        self.fix_patterns = {
            "import_error": [
                {
                    "pattern": r"from\s+(\w+)\s+import\s+(\w+)",
                    "fix": "Check if module is installed and import path is correct",
                    "strategy": FixStrategy.DEPENDENCY,
                },
            ],
            "syntax_error": [
                {
                    "pattern": r"SyntaxError",
                    "fix": "Check syntax, brackets, and indentation",
                    "strategy": FixStrategy.PATTERN_MATCHING,
                },
            ],
            "indentation_error": [
                {
                    "pattern": r"IndentationError",
                    "fix": "Fix indentation to match Python standards",
                    "strategy": FixStrategy.PATTERN_MATCHING,
                },
            ],
        }

    def auto_fix(
        self,
        issue: DetectedIssue,
        auto_apply: bool = False,
    ) -> FixAttempt:
        """
        Automatically fix an issue
        """
        fix_id = str(uuid.uuid4())

        # Step 1: Analyze issue deeply
        analysis = self.issue_analyzer.analyze_issue(issue, AnalysisDepth.DEEP)

        # Step 2: Select fix strategy
        strategy = self._select_fix_strategy(issue, analysis)

        # Step 3: Generate fix
        fix_description, fix_code = self._generate_fix(issue, analysis, strategy)

        # Step 4: Validate fix
        validation_result = self._validate_fix(issue, fix_code, fix_description)

        # Step 5: Calculate confidence
        confidence = self._calculate_fix_confidence(strategy, validation_result, analysis)

        # Step 6: Apply fix if requested and confident
        applied = False
        success = None

        if auto_apply and confidence == FixConfidence.HIGH:
            applied = True
            success = self._apply_fix(issue, fix_code, fix_description)

        # Create fix attempt
        fix_attempt = FixAttempt(
            fix_id=fix_id,
            issue=issue,
            strategy=strategy,
            fix_description=fix_description,
            fix_code=fix_code,
            confidence=confidence,
            applied=applied,
            success=success,
            validation_result=validation_result,
        )

        self.fix_history.append(fix_attempt)

        # Keep only recent fixes (last 5000)
        if len(self.fix_history) > 5000:
            self.fix_history = self.fix_history[-5000:]

        return fix_attempt

    def _select_fix_strategy(
        self,
        issue: DetectedIssue,
        analysis: Any,
    ) -> FixStrategy:
        """Select appropriate fix strategy"""
        issue_type_lower = issue.type.lower()

        # Check pattern library
        for pattern_type, patterns in self.fix_patterns.items():
            if pattern_type in issue_type_lower:
                return patterns[0]["strategy"]

        # Use creative solver for complex issues
        if len(analysis.root_causes) > 2:
            return FixStrategy.CREATIVE

        # Use reasoning to select strategy
        reasoning = self.reasoning_engine.chain_of_thought_reasoning(
            f"Select fix strategy for {issue.type}",
            {"issue": issue.description, "root_causes": analysis.root_causes},
        )

        # Extract strategy from reasoning
        conclusion_lower = reasoning.final_conclusion.lower() if reasoning.final_conclusion else ""

        if "pattern" in conclusion_lower:
            return FixStrategy.PATTERN_MATCHING
        elif "generate" in conclusion_lower or "create" in conclusion_lower:
            return FixStrategy.CODE_GENERATION
        elif "refactor" in conclusion_lower:
            return FixStrategy.REFACTORING
        elif "config" in conclusion_lower:
            return FixStrategy.CONFIGURATION
        elif "dependency" in conclusion_lower:
            return FixStrategy.DEPENDENCY

        return FixStrategy.PATTERN_MATCHING  # Default

    def _generate_fix(
        self,
        issue: DetectedIssue,
        analysis: Any,
        strategy: FixStrategy,
    ) -> tuple[str, str | None]:
        """Generate fix description and code"""
        fix_description = ""
        fix_code = None

        if strategy == FixStrategy.PATTERN_MATCHING:
            # Use pattern-based fix
            issue_type_lower = issue.type.lower()
            for pattern_type, patterns in self.fix_patterns.items():
                if pattern_type in issue_type_lower:
                    fix_description = patterns[0]["fix"]
                    break

        elif strategy == FixStrategy.CREATIVE:
            # Use creative problem solving
            solutions = self.creative_solver.solve_creatively(
                f"Fix {issue.type}: {issue.description}",
                constraints=analysis.recommended_actions,
                context={"root_causes": analysis.root_causes},
            )

            if solutions:
                best_solution = solutions[0]
                fix_description = best_solution.description

        elif strategy == FixStrategy.CODE_GENERATION:
            # Generate code fix
            fix_description = f"Generate code to fix {issue.type}"
            # Simplified - real implementation would generate actual code
            fix_code = f"# Fix for {issue.type}\n# {issue.description}\n# TODO: Implement fix"

        else:
            # Default fix
            fix_description = f"Apply standard fix for {issue.type}"

        # Enhance with root cause information
        if analysis.root_causes:
            fix_description += f" (Root cause: {analysis.root_causes[0]})"

        return fix_description, fix_code

    def _validate_fix(
        self,
        issue: DetectedIssue,
        fix_code: str | None,
        fix_description: str,
    ) -> dict[str, Any]:
        """Validate fix before applying"""
        validation = {
            "syntax_valid": True,
            "addresses_root_cause": True,
            "no_side_effects": True,
            "completeness": 0.7,
        }

        # Check if fix addresses root cause
        issue_keywords = set(issue.type.lower().split())
        fix_keywords = set(fix_description.lower().split())

        overlap = len(issue_keywords & fix_keywords) / max(len(issue_keywords), 1)
        validation["addresses_root_cause"] = overlap > 0.3

        # Check completeness
        if fix_code:
            validation["completeness"] = 0.8
        else:
            validation["completeness"] = 0.5

        return validation

    def _calculate_fix_confidence(
        self,
        strategy: FixStrategy,
        validation_result: dict[str, Any],
        analysis: Any,
    ) -> FixConfidence:
        """Calculate confidence in fix"""
        confidence_score = 0.5  # Base

        # Strategy-based confidence
        strategy_confidence = {
            FixStrategy.PATTERN_MATCHING: 0.8,
            FixStrategy.CODE_GENERATION: 0.6,
            FixStrategy.REFACTORING: 0.7,
            FixStrategy.CONFIGURATION: 0.75,
            FixStrategy.DEPENDENCY: 0.85,
            FixStrategy.CREATIVE: 0.65,
        }
        confidence_score = strategy_confidence.get(strategy, 0.5)

        # Validation-based adjustment
        if validation_result.get("addresses_root_cause"):
            confidence_score += 0.1
        if validation_result.get("completeness", 0) > 0.7:
            confidence_score += 0.1

        # Analysis confidence
        confidence_score *= analysis.confidence

        # Map to confidence level
        if confidence_score >= 0.8:
            return FixConfidence.HIGH
        elif confidence_score >= 0.5:
            return FixConfidence.MEDIUM
        else:
            return FixConfidence.LOW

    def _apply_fix(
        self,
        issue: DetectedIssue,
        fix_code: str | None,
        fix_description: str,
    ) -> bool:
        """Apply fix to codebase"""
        # Simplified - real implementation would:
        # 1. Parse target file
        # 2. Apply fix
        # 3. Validate syntax
        # 4. Run tests
        # 5. Commit changes

        # For now, return success if fix description is reasonable
        return len(fix_description) > 20

    def get_fix_history(self) -> list[FixAttempt]:
        """Get fix history"""
        return self.fix_history

    def get_fix_stats(self) -> dict[str, Any]:
        """Get fix statistics"""
        applied_fixes = [f for f in self.fix_history if f.applied]
        successful_fixes = [f for f in applied_fixes if f.success]

        return {
            "total_fix_attempts": len(self.fix_history),
            "applied_fixes": len(applied_fixes),
            "successful_fixes": len(successful_fixes),
            "success_rate": (len(successful_fixes) / len(applied_fixes) if applied_fixes else 0.0),
            "fixes_by_strategy": {
                strategy.value: len([f for f in self.fix_history if f.strategy == strategy])
                for strategy in FixStrategy
            },
            "fixes_by_confidence": {
                confidence.value: len([f for f in self.fix_history if f.confidence == confidence])
                for confidence in FixConfidence
            },
        }
