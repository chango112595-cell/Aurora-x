"""
User Preference Learning System
Self-contained user preference learning and adaptation
No external APIs - uses behavior analysis, pattern recognition, and preference extraction
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserPreference:
    """User preference"""

    category: str
    preference: str
    confidence: float
    last_updated: datetime = field(default_factory=datetime.now)
    usage_count: int = 1


@dataclass
class UserBehavior:
    """User behavior record"""

    action: str
    context: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    outcome: str | None = None


class UserPreferenceLearner:
    """
    Self-contained user preference learning system
    Learns and adapts to user preferences from behavior analysis
    """

    def __init__(self):
        self.preferences: dict[str, list[UserPreference]] = defaultdict(list)
        self.behavior_history: list[UserBehavior] = []
        self.patterns: dict[str, dict[str, Any]] = {}

    def record_behavior(self, action: str, context: dict[str, Any], outcome: str | None = None):
        """Record user behavior"""
        behavior = UserBehavior(
            action=action,
            context=context,
            outcome=outcome,
        )
        self.behavior_history.append(behavior)

        # Keep only recent history (last 10000)
        if len(self.behavior_history) > 10000:
            self.behavior_history = self.behavior_history[-10000:]

        # Update preferences based on behavior
        self._update_preferences_from_behavior(behavior)

    def _update_preferences_from_behavior(self, behavior: UserBehavior):
        """Update preferences from behavior"""
        # Extract preferences from behavior patterns
        action_type = behavior.action.split("_")[0] if "_" in behavior.action else behavior.action

        # Analyze context for preferences
        if "format" in behavior.context:
            self._update_preference("output_format", behavior.context["format"], 0.1)

        if "style" in behavior.context:
            self._update_preference("code_style", behavior.context["style"], 0.1)

        if "detail_level" in behavior.context:
            self._update_preference("detail_level", behavior.context["detail_level"], 0.1)

        # Positive outcome increases confidence
        if behavior.outcome == "success" or behavior.outcome == "positive":
            for pref in self.preferences.get(action_type, []):
                pref.confidence = min(1.0, pref.confidence + 0.05)

    def _update_preference(self, category: str, preference: str, confidence_delta: float):
        """Update or create preference"""
        category_prefs = self.preferences[category]

        # Find existing preference
        existing = None
        for pref in category_prefs:
            if pref.preference == preference:
                existing = pref
                break

        if existing:
            existing.confidence = min(1.0, existing.confidence + confidence_delta)
            existing.usage_count += 1
            existing.last_updated = datetime.now()
        else:
            category_prefs.append(
                UserPreference(
                    category=category,
                    preference=preference,
                    confidence=confidence_delta,
                )
            )

    def get_preference(self, category: str, default: str | None = None) -> str | None:
        """Get user preference for category"""
        category_prefs = self.preferences.get(category, [])

        if not category_prefs:
            return default

        # Return preference with highest confidence
        best_pref = max(category_prefs, key=lambda p: p.confidence)

        # Only return if confidence is above threshold
        if best_pref.confidence > 0.3:
            return best_pref.preference

        return default

    def analyze_behavior_patterns(self) -> dict[str, Any]:
        """Analyze user behavior patterns"""
        patterns: dict[str, Any] = {
            "frequent_actions": defaultdict(int),
            "time_patterns": defaultdict(int),
            "context_patterns": defaultdict(int),
        }

        for behavior in self.behavior_history[-1000:]:  # Last 1000 behaviors
            # Count frequent actions
            patterns["frequent_actions"][behavior.action] += 1

            # Analyze time patterns
            hour = behavior.timestamp.hour
            if 6 <= hour < 12:
                time_slot = "morning"
            elif 12 <= hour < 18:
                time_slot = "afternoon"
            elif 18 <= hour < 22:
                time_slot = "evening"
            else:
                time_slot = "night"
            patterns["time_patterns"][time_slot] += 1

            # Analyze context patterns
            for key, value in behavior.context.items():
                patterns["context_patterns"][f"{key}:{value}"] += 1

        # Store patterns
        self.patterns = patterns

        return patterns

    def personalize_response(self, base_response: dict[str, Any]) -> dict[str, Any]:
        """Personalize response based on preferences"""
        personalized = base_response.copy()

        # Apply format preference
        format_pref = self.get_preference("output_format")
        if format_pref:
            personalized["format"] = format_pref

        # Apply detail level preference
        detail_pref = self.get_preference("detail_level")
        if detail_pref:
            personalized["detail_level"] = detail_pref

        # Apply code style preference
        style_pref = self.get_preference("code_style")
        if style_pref:
            personalized["code_style"] = style_pref

        return personalized

    def learn_workflow(self, workflow_steps: list[dict[str, Any]]):
        """Learn a custom workflow"""
        workflow_id = f"workflow_{len(self.patterns)}"

        self.patterns[workflow_id] = {
            "steps": workflow_steps,
            "usage_count": 1,
            "last_used": datetime.now(),
        }

    def get_learned_workflows(self) -> list[dict[str, Any]]:
        """Get learned workflows"""
        workflows = []

        for workflow_id, workflow_data in self.patterns.items():
            if workflow_id.startswith("workflow_"):
                workflows.append(
                    {
                        "id": workflow_id,
                        "steps": workflow_data.get("steps", []),
                        "usage_count": workflow_data.get("usage_count", 0),
                        "last_used": workflow_data.get("last_used"),
                    }
                )

        return workflows

    def get_preference_summary(self) -> dict[str, Any]:
        """Get summary of all preferences"""
        summary = {
            "total_preferences": sum(len(prefs) for prefs in self.preferences.values()),
            "categories": list(self.preferences.keys()),
            "preferences_by_category": {},
            "behavior_history_size": len(self.behavior_history),
        }

        for category, prefs in self.preferences.items():
            summary["preferences_by_category"][category] = [
                {
                    "preference": pref.preference,
                    "confidence": pref.confidence,
                    "usage_count": pref.usage_count,
                }
                for pref in sorted(prefs, key=lambda p: p.confidence, reverse=True)
            ]

        return summary
