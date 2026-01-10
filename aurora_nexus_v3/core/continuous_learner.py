"""
Continuous Learning System
Self-contained learning from all interactions and experiences
No external APIs - uses pattern extraction, experience replay, and knowledge consolidation
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class LearningType(Enum):
    """Types of learning"""

    PATTERN_EXTRACTION = "pattern_extraction"
    STRATEGY_REFINEMENT = "strategy_refinement"
    KNOWLEDGE_CONSOLIDATION = "knowledge_consolidation"
    EXPERIENCE_REPLAY = "experience_replay"
    TRANSFER_LEARNING = "transfer_learning"


@dataclass
class LearningExperience:
    """A single learning experience"""

    experience_id: str
    learning_type: LearningType
    context: dict[str, Any]
    action: str
    outcome: dict[str, Any]
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    extracted_patterns: list[str] = field(default_factory=list)
    learned_strategy: str | None = None


@dataclass
class LearnedPattern:
    """A learned pattern"""

    pattern_id: str
    pattern_type: str
    pattern_description: str
    occurrences: int
    success_rate: float
    contexts: list[dict[str, Any]] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)


class ContinuousLearner:
    """
    Self-contained continuous learning system
    Learns from all interactions and improves over time
    """

    def __init__(self, learning_data_dir: str = "data/learning"):
        self.learning_data_dir = Path(learning_data_dir)
        self.learning_data_dir.mkdir(parents=True, exist_ok=True)

        self.experiences: list[LearningExperience] = []
        self.learned_patterns: dict[str, LearnedPattern] = {}
        self.strategy_library: dict[
            str, dict[str, Any]
        ] = {}  # task_type -> {strategy, success_rate}
        self.knowledge_base: dict[str, list[str]] = {}  # concept -> [knowledge]
        self.transfer_mappings: dict[
            str, dict[str, str]
        ] = {}  # source_domain -> {target_domain: mapping}

        # Load existing learning data
        self._load_learning_data()

    def learn_from_experience(
        self,
        context: dict[str, Any],
        action: str,
        outcome: dict[str, Any],
        success: bool,
    ) -> LearningExperience:
        """Learn from a single experience"""
        import uuid

        experience = LearningExperience(
            experience_id=str(uuid.uuid4()),
            learning_type=LearningType.PATTERN_EXTRACTION,
            context=context,
            action=action,
            outcome=outcome,
            success=success,
        )

        # Extract patterns
        patterns = self._extract_patterns(context, action, outcome, success)
        experience.extracted_patterns = patterns

        # Refine strategies
        strategy = self._refine_strategy(context, action, success)
        experience.learned_strategy = strategy

        # Store experience
        self.experiences.append(experience)

        # Update learned patterns
        self._update_patterns(patterns, context, success)

        # Consolidate knowledge
        self._consolidate_knowledge(experience)

        # Keep only recent experiences (last 10000)
        if len(self.experiences) > 10000:
            self.experiences = self.experiences[-10000:]

        # Save learning data periodically
        if len(self.experiences) % 100 == 0:
            self._save_learning_data()

        return experience

    def get_best_strategy(
        self, task_type: str, context: dict[str, Any] = None
    ) -> dict[str, Any] | None:
        """Get best strategy for a task type"""
        if task_type not in self.strategy_library:
            return None

        strategy_info = self.strategy_library[task_type]

        # If context provided, find most similar strategy
        if context:
            best_match = self._find_similar_strategy(task_type, context)
            if best_match:
                return best_match

        return strategy_info

    def get_relevant_patterns(
        self, context: dict[str, Any], min_success_rate: float = 0.7
    ) -> list[LearnedPattern]:
        """Get relevant patterns for context"""
        relevant = []

        # Extract key concepts from context
        context_concepts = self._extract_concepts(str(context))

        for pattern in self.learned_patterns.values():
            # Check if pattern is relevant
            pattern_concepts = self._extract_concepts(pattern.pattern_description)

            # Calculate relevance (concept overlap)
            overlap = len(set(context_concepts) & set(pattern_concepts))
            relevance = overlap / max(len(context_concepts), len(pattern_concepts), 1)

            if relevance > 0.3 and pattern.success_rate >= min_success_rate:
                relevant.append(pattern)

        # Sort by relevance and success rate
        relevant.sort(key=lambda p: (p.success_rate, p.occurrences), reverse=True)

        return relevant[:10]  # Top 10

    def transfer_knowledge(self, source_domain: str, target_domain: str) -> dict[str, Any]:
        """Transfer knowledge from source to target domain"""
        # Find patterns in source domain
        source_patterns = [
            p
            for p in self.learned_patterns.values()
            if source_domain.lower() in p.pattern_description.lower()
        ]

        # Create mappings
        mappings = {}
        for pattern in source_patterns[:5]:  # Top 5 patterns
            # Adapt pattern to target domain
            adapted = self._adapt_pattern(pattern, target_domain)
            mappings[pattern.pattern_id] = adapted

        # Store transfer mapping
        if source_domain not in self.transfer_mappings:
            self.transfer_mappings[source_domain] = {}
        self.transfer_mappings[source_domain][target_domain] = mappings

        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "patterns_transferred": len(mappings),
            "mappings": mappings,
        }

    def _extract_patterns(
        self,
        context: dict[str, Any],
        action: str,
        outcome: dict[str, Any],
        success: bool,
    ) -> list[str]:
        """Extract patterns from experience"""
        patterns = []

        # Pattern 1: Action-outcome correlation
        if success:
            patterns.append(f"Action '{action}' leads to success in similar contexts")
        else:
            patterns.append(f"Action '{action}' leads to failure in similar contexts")

        # Pattern 2: Context-action correlation
        context_str = str(context)
        if "error" in context_str.lower() and success:
            patterns.append("Error contexts can be resolved with appropriate actions")

        # Pattern 3: Outcome patterns
        if "time" in outcome:
            patterns.append(f"Action '{action}' takes {outcome.get('time', 0)}ms")

        return patterns

    def _refine_strategy(self, context: dict[str, Any], action: str, success: bool) -> str | None:
        """Refine strategy based on experience"""
        # Identify task type from context
        task_type = context.get("task_type", "general")

        if task_type not in self.strategy_library:
            self.strategy_library[task_type] = {
                "strategy": action,
                "success_count": 1 if success else 0,
                "total_count": 1,
                "success_rate": 1.0 if success else 0.0,
            }
            return action

        # Update strategy statistics
        strategy_info = self.strategy_library[task_type]
        strategy_info["total_count"] += 1
        if success:
            strategy_info["success_count"] += 1

        strategy_info["success_rate"] = (
            strategy_info["success_count"] / strategy_info["total_count"]
        )

        # If this action is better, update strategy
        if success and action != strategy_info["strategy"]:
            # Check if we should switch strategies
            current_success_rate = strategy_info["success_rate"]

            # If new action seems promising, consider switching
            # (This is simplified - real implementation would use more sophisticated comparison)
            if current_success_rate < 0.5:  # Current strategy not great
                strategy_info["strategy"] = action
                return action

        return strategy_info["strategy"]

    def _update_patterns(self, patterns: list[str], context: dict[str, Any], success: bool):
        """Update learned patterns"""
        for pattern_desc in patterns:
            # Create pattern key
            pattern_key = self._create_pattern_key(pattern_desc)

            if pattern_key not in self.learned_patterns:
                import uuid

                self.learned_patterns[pattern_key] = LearnedPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type=self._classify_pattern(pattern_desc),
                    pattern_description=pattern_desc,
                    occurrences=1,
                    success_rate=1.0 if success else 0.0,
                    contexts=[context],
                )
            else:
                pattern = self.learned_patterns[pattern_key]
                pattern.occurrences += 1
                pattern.contexts.append(context)
                pattern.last_seen = datetime.now()

                # Update success rate
                total_successes = pattern.success_rate * (pattern.occurrences - 1)
                if success:
                    total_successes += 1
                pattern.success_rate = total_successes / pattern.occurrences

                # Keep only recent contexts (last 100)
                if len(pattern.contexts) > 100:
                    pattern.contexts = pattern.contexts[-100:]

    def _consolidate_knowledge(self, experience: LearningExperience):
        """Consolidate knowledge from experience"""
        # Extract key concepts
        concepts = self._extract_concepts(str(experience.context) + " " + experience.action)

        # Store knowledge
        for concept in concepts:
            if concept not in self.knowledge_base:
                self.knowledge_base[concept] = []

            # Add new knowledge
            knowledge_entry = (
                f"{experience.action} -> {'success' if experience.success else 'failure'}"
            )
            if knowledge_entry not in self.knowledge_base[concept]:
                self.knowledge_base[concept].append(knowledge_entry)

            # Keep only recent knowledge (last 50 per concept)
            if len(self.knowledge_base[concept]) > 50:
                self.knowledge_base[concept] = self.knowledge_base[concept][-50:]

    def _find_similar_strategy(
        self, task_type: str, context: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Find similar strategy based on context"""
        # Simple similarity check using concept overlap
        # (Simplified - full implementation would use embedding similarity)

        # For now, return the strategy for this task type if available
        return self.strategy_library.get(task_type)

    def _adapt_pattern(self, pattern: LearnedPattern, target_domain: str) -> str:
        """Adapt a pattern to target domain"""
        # Simple adaptation - replace domain-specific terms
        adapted = pattern.pattern_description

        # Extract source domain from pattern
        # (Simplified - real implementation would be more sophisticated)

        return adapted

    def _create_pattern_key(self, pattern_desc: str) -> str:
        """Create a key for pattern"""
        # Use first 50 characters as key
        return pattern_desc[:50].lower().replace(" ", "_")

    def _classify_pattern(self, pattern_desc: str) -> str:
        """Classify pattern type"""
        desc_lower = pattern_desc.lower()

        if "leads to" in desc_lower or "causes" in desc_lower:
            return "causal"
        elif "takes" in desc_lower or "duration" in desc_lower:
            return "temporal"
        elif "in context" in desc_lower:
            return "contextual"
        else:
            return "general"

    def _extract_concepts(self, text: str) -> list[str]:
        """Extract key concepts from text"""
        # Simple concept extraction
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

        # Filter out common words
        stop_words = {
            "that",
            "this",
            "with",
            "from",
            "have",
            "been",
            "will",
            "would",
            "could",
            "should",
            "action",
            "context",
            "outcome",
            "success",
        }

        concepts = [w for w in words if w not in stop_words]
        return list(set(concepts))[:10]  # Top 10 unique concepts

    def _load_learning_data(self):
        """Load learning data from disk"""
        learning_file = self.learning_data_dir / "learning_data.json"
        if learning_file.exists():
            try:
                with open(learning_file, encoding="utf-8") as f:
                    json.load(f)  # Load data (simplified - full implementation would restore state)
                    # Load patterns and strategies
                    # (Simplified - full implementation would load all data)
            except Exception:
                pass  # Start fresh if load fails

    def _save_learning_data(self):
        """Save learning data to disk"""
        learning_file = self.learning_data_dir / "learning_data.json"
        try:
            data = {
                "patterns": {
                    pid: {
                        "pattern_type": p.pattern_type,
                        "pattern_description": p.pattern_description,
                        "occurrences": p.occurrences,
                        "success_rate": p.success_rate,
                    }
                    for pid, p in self.learned_patterns.items()
                },
                "strategies": self.strategy_library,
                "knowledge_base_size": sum(len(v) for v in self.knowledge_base.values()),
            }
            with open(learning_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass  # Continue if save fails

    def get_learning_stats(self) -> dict[str, Any]:
        """Get learning statistics"""
        return {
            "total_experiences": len(self.experiences),
            "learned_patterns": len(self.learned_patterns),
            "strategies_learned": len(self.strategy_library),
            "knowledge_concepts": len(self.knowledge_base),
            "transfer_mappings": len(self.transfer_mappings),
            "average_pattern_success_rate": (
                sum(p.success_rate for p in self.learned_patterns.values())
                / len(self.learned_patterns)
                if self.learned_patterns
                else 0.0
            ),
        }
