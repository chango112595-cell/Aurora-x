"""
Intelligent Task Decomposition System
Self-contained automatic task breakdown with dependency resolution
No external APIs - uses graph algorithms and pattern matching
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..workers.worker import Task, TaskType


class DependencyType(Enum):
    """Types of dependencies between tasks"""

    REQUIRES = "requires"  # Task A requires Task B to complete first
    ENHANCES = "enhances"  # Task A enhances Task B (can run in parallel but B benefits from A)
    CONFLICTS = "conflicts"  # Task A conflicts with Task B (cannot run simultaneously)
    INDEPENDENT = "independent"  # No dependency


@dataclass
class Subtask:
    """A decomposed subtask"""

    subtask_id: str
    parent_task_id: str
    description: str
    task_type: TaskType
    priority: int
    estimated_duration_ms: int
    dependencies: list[str] = field(default_factory=list)  # Other subtask IDs this depends on
    resources_needed: list[str] = field(default_factory=list)
    can_parallelize: bool = True


@dataclass
class TaskDecomposition:
    """Complete task decomposition"""

    decomposition_id: str
    original_task: Task
    subtasks: list[Subtask] = field(default_factory=list)
    dependency_graph: dict[str, list[str]] = field(
        default_factory=dict
    )  # subtask_id -> [dependent_subtask_ids]
    execution_order: list[list[str]] = field(default_factory=list)  # List of parallel groups
    total_estimated_duration_ms: int = 0


class IntelligentTaskDecomposer:
    """
    Self-contained intelligent task decomposition system
    Automatically breaks down complex tasks into manageable subtasks
    """

    def __init__(self):
        self.decomposition_history: list[TaskDecomposition] = []
        self.pattern_library: dict[str, list[str]] = {}  # task_pattern -> [decomposition_patterns]
        self.dependency_patterns: dict[str, list[str]] = {}  # dependency_type -> [patterns]
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize decomposition patterns"""
        self.pattern_library = {
            "code_generation": [
                "analyze_requirements",
                "design_structure",
                "implement_core",
                "add_tests",
                "document",
            ],
            "bug_fixing": [
                "reproduce_issue",
                "identify_root_cause",
                "design_fix",
                "implement_fix",
                "test_fix",
                "verify_fix",
            ],
            "refactoring": [
                "analyze_current_code",
                "identify_refactoring_opportunities",
                "plan_refactoring",
                "execute_refactoring",
                "verify_functionality",
            ],
            "optimization": [
                "profile_performance",
                "identify_bottlenecks",
                "design_optimization",
                "implement_optimization",
                "measure_improvement",
            ],
        }

        self.dependency_patterns = {
            "requires": [
                r"(\w+)\s+requires\s+(\w+)",
                r"(\w+)\s+needs\s+(\w+)",
                r"(\w+)\s+depends\s+on\s+(\w+)",
                r"before\s+(\w+)\s+do\s+(\w+)",
            ],
            "enhances": [
                r"(\w+)\s+improves\s+(\w+)",
                r"(\w+)\s+enhances\s+(\w+)",
            ],
            "conflicts": [
                r"(\w+)\s+conflicts\s+with\s+(\w+)",
                r"(\w+)\s+cannot\s+run\s+with\s+(\w+)",
            ],
        }

    def decompose_task(self, task: Task, context: dict[str, Any] = None) -> TaskDecomposition:
        """
        Decompose a complex task into subtasks
        """
        context = context or {}
        decomposition_id = str(uuid.uuid4())

        decomposition = TaskDecomposition(
            decomposition_id=decomposition_id,
            original_task=task,
        )

        # Identify task pattern
        task_pattern = self._identify_task_pattern(task)

        # Generate subtasks based on pattern
        subtask_descriptions = self._generate_subtasks(task, task_pattern)

        # Create subtask objects
        for i, desc in enumerate(subtask_descriptions):
            subtask = Subtask(
                subtask_id=f"{decomposition_id}-subtask-{i}",
                parent_task_id=task.id,
                description=desc,
                task_type=self._determine_subtask_type(desc, task.task_type),
                priority=self._calculate_subtask_priority(
                    desc, task.priority, i, len(subtask_descriptions)
                ),
                estimated_duration_ms=self._estimate_duration(desc),
                can_parallelize=self._can_parallelize(desc, subtask_descriptions, i),
            )
            decomposition.subtasks.append(subtask)

        # Identify dependencies
        self._identify_dependencies(decomposition)

        # Build dependency graph
        self._build_dependency_graph(decomposition)

        # Calculate execution order (parallel groups)
        self._calculate_execution_order(decomposition)

        # Calculate total estimated duration
        decomposition.total_estimated_duration_ms = self._calculate_total_duration(decomposition)

        self.decomposition_history.append(decomposition)
        return decomposition

    def _identify_task_pattern(self, task: Task) -> str:
        """Identify the pattern of the task"""
        payload_str = str(task.payload).lower()
        task_type_str = task.task_type.value.lower()

        # Check against known patterns
        for pattern, _ in self.pattern_library.items():
            if pattern in payload_str or pattern in task_type_str:
                return pattern

        # Default patterns based on task type
        type_patterns = {
            TaskType.CODE: "code_generation",
            TaskType.FIX: "bug_fixing",
            TaskType.OPTIMIZE: "optimization",
            TaskType.ANALYZE: "code_generation",  # Analysis often involves generation
        }

        return type_patterns.get(task.task_type, "general")

    def _generate_subtasks(self, task: Task, pattern: str) -> list[str]:
        """Generate subtasks based on pattern"""
        # Get pattern-specific subtasks
        if pattern in self.pattern_library:
            base_subtasks = self.pattern_library[pattern].copy()
        else:
            # Generic decomposition
            base_subtasks = [
                "analyze_requirements",
                "design_solution",
                "implement_solution",
                "test_solution",
                "verify_solution",
            ]

        # Customize based on task payload
        customized = []
        payload_str = str(task.payload).lower()

        for subtask_template in base_subtasks:
            # Customize subtask description
            customized_desc = self._customize_subtask(subtask_template, task.payload, payload_str)
            customized.append(customized_desc)

        return customized

    def _customize_subtask(self, template: str, payload: dict[str, Any], payload_str: str) -> str:
        """Customize subtask description based on payload"""
        # Extract key terms from payload
        target = payload.get("target", "")
        action = payload.get("action", "")

        if target:
            return f"{template.replace('_', ' ').title()} for {target}"
        elif action:
            return f"{template.replace('_', ' ').title()} to {action}"
        else:
            return template.replace("_", " ").title()

    def _determine_subtask_type(self, description: str, parent_type: TaskType) -> TaskType:
        """Determine the type of subtask"""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ["fix", "bug", "error", "issue"]):
            return TaskType.FIX
        elif any(word in desc_lower for word in ["analyze", "examine", "review"]):
            return TaskType.ANALYZE
        elif any(word in desc_lower for word in ["optimize", "improve", "enhance"]):
            return TaskType.OPTIMIZE
        elif any(word in desc_lower for word in ["test", "verify", "validate"]):
            return TaskType.MONITOR
        else:
            return parent_type

    def _calculate_subtask_priority(
        self, description: str, parent_priority: int, index: int, total: int
    ) -> int:
        """Calculate priority for subtask"""
        # Earlier subtasks typically have higher priority
        priority_adjustment = (total - index) * 2

        # Some subtasks are more critical
        desc_lower = description.lower()
        if any(word in desc_lower for word in ["critical", "core", "essential", "foundation"]):
            priority_adjustment += 5

        return max(1, min(10, parent_priority - priority_adjustment // total))

    def _estimate_duration(self, description: str) -> int:
        """Estimate duration in milliseconds"""
        desc_lower = description.lower()

        # Base duration estimates
        if any(word in desc_lower for word in ["analyze", "examine"]):
            return 5000  # 5 seconds
        elif any(word in desc_lower for word in ["design", "plan"]):
            return 10000  # 10 seconds
        elif any(word in desc_lower for word in ["implement", "create", "build"]):
            return 30000  # 30 seconds
        elif any(word in desc_lower for word in ["test", "verify"]):
            return 15000  # 15 seconds
        else:
            return 10000  # Default 10 seconds

    def _can_parallelize(self, description: str, all_subtasks: list[str], index: int) -> bool:
        """Determine if subtask can run in parallel"""
        desc_lower = description.lower()

        # Some tasks cannot be parallelized
        if any(word in desc_lower for word in ["requires", "depends", "after", "then"]):
            return False

        # Analysis tasks can often run in parallel
        if any(word in desc_lower for word in ["analyze", "examine", "review"]):
            return True

        # Later tasks might depend on earlier ones
        if index < len(all_subtasks) // 2:
            return True

        return True  # Default to parallelizable

    def _identify_dependencies(self, decomposition: TaskDecomposition):
        """Identify dependencies between subtasks"""
        subtasks = decomposition.subtasks

        for i, subtask1 in enumerate(subtasks):
            for j, subtask2 in enumerate(subtasks):
                if i == j:
                    continue

                # Check for dependency patterns
                dep_type = self._check_dependency(subtask1.description, subtask2.description)

                if dep_type == DependencyType.REQUIRES:
                    if subtask2.subtask_id not in subtask1.dependencies:
                        subtask1.dependencies.append(subtask2.subtask_id)
                elif dep_type == DependencyType.CONFLICTS:
                    subtask1.can_parallelize = False
                    subtask2.can_parallelize = False

    def _check_dependency(self, desc1: str, desc2: str) -> DependencyType:
        """Check dependency type between two subtasks"""
        desc1_lower = desc1.lower()
        desc2_lower = desc2.lower()

        # Extract key concepts
        concepts1 = set(desc1_lower.split())
        set(desc2_lower.split())

        # Check for explicit dependency patterns
        if "requires" in desc1_lower and any(c in desc2_lower for c in concepts1):
            return DependencyType.REQUIRES

        # Check for sequential patterns
        desc1_lower.split()
        desc2_lower.split()

        sequential_keywords = ["before", "after", "then", "next", "followed"]
        if any(kw in desc1_lower for kw in sequential_keywords):
            return DependencyType.REQUIRES

        # Check for conflicts
        conflict_keywords = ["conflicts", "cannot", "incompatible"]
        if any(kw in desc1_lower for kw in conflict_keywords):
            return DependencyType.CONFLICTS

        return DependencyType.INDEPENDENT

    def _build_dependency_graph(self, decomposition: TaskDecomposition):
        """Build dependency graph"""
        for subtask in decomposition.subtasks:
            decomposition.dependency_graph[subtask.subtask_id] = subtask.dependencies

    def _calculate_execution_order(self, decomposition: TaskDecomposition):
        """Calculate execution order with parallelization"""
        # Topological sort to find execution order
        subtasks = {st.subtask_id: st for st in decomposition.subtasks}
        in_degree = {st_id: len(st.dependencies) for st_id, st in subtasks.items()}

        execution_order = []
        ready_queue = [st_id for st_id, degree in in_degree.items() if degree == 0]

        while ready_queue:
            # Current parallel group
            current_group = ready_queue[:]
            ready_queue = []
            execution_order.append(current_group)

            # Process current group
            for st_id in current_group:
                # Find subtasks that depend on this one
                for dependent_id, dependent_st in subtasks.items():
                    if st_id in dependent_st.dependencies:
                        in_degree[dependent_id] -= 1
                        if in_degree[dependent_id] == 0:
                            ready_queue.append(dependent_id)

        decomposition.execution_order = execution_order

    def _calculate_total_duration(self, decomposition: TaskDecomposition) -> int:
        """Calculate total estimated duration"""
        total = 0

        for parallel_group in decomposition.execution_order:
            # Duration of parallel group is max of subtasks in group
            group_duration = 0
            for st_id in parallel_group:
                subtask = next(
                    (st for st in decomposition.subtasks if st.subtask_id == st_id), None
                )
                if subtask:
                    group_duration = max(group_duration, subtask.estimated_duration_ms)
            total += group_duration

        return total

    def get_decomposition_history(self) -> list[TaskDecomposition]:
        """Get decomposition history"""
        return self.decomposition_history

    def get_status(self) -> dict[str, Any]:
        """Get decomposer status"""
        return {
            "decompositions_performed": len(self.decomposition_history),
            "patterns_available": list(self.pattern_library.keys()),
            "average_subtasks_per_task": sum(len(d.subtasks) for d in self.decomposition_history)
            / len(self.decomposition_history)
            if self.decomposition_history
            else 0,
        }
