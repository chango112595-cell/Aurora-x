"""
Aurora Creative Problem-Solving Engine
Self-contained generative creativity and novel solution discovery
No external APIs - uses pattern combination, constraint relaxation, and synthesis
"""

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CreativityTechnique(Enum):
    """Creative problem-solving techniques"""

    DIVERGENT_THINKING = "divergent_thinking"
    CONSTRAINT_RELAXATION = "constraint_relaxation"
    CROSS_DOMAIN_TRANSFER = "cross_domain_transfer"
    COMBINATORIAL_SYNTHESIS = "combinatorial_synthesis"
    ANALOGICAL_REASONING = "analogical_reasoning"
    REVERSE_THINKING = "reverse_thinking"


@dataclass
class Solution:
    """A generated solution"""

    solution_id: str
    description: str
    technique: CreativityTechnique
    novelty_score: float
    feasibility_score: float
    combined_score: float
    constraints_relaxed: list[str] = field(default_factory=list)
    domains_combined: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class CreativeProblemSolver:
    """
    Self-contained creative problem-solving engine
    Generates novel solutions through various creative techniques
    """

    def __init__(self):
        self.solution_history: list[Solution] = []
        self.domain_knowledge: dict[str, list[str]] = {}  # domain -> [techniques]
        self.constraint_patterns: dict[str, list[str]] = {}  # constraint_type -> [patterns]
        self.analogy_database: dict[str, list[str]] = {}  # problem_type -> [analogies]
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize creative patterns"""
        self.constraint_patterns = {
            "resource": ["limited", "insufficient", "not enough", "lack of"],
            "time": ["urgent", "deadline", "quick", "fast"],
            "technical": ["cannot", "impossible", "not supported", "incompatible"],
            "cost": ["expensive", "costly", "budget", "affordable"],
        }

        self.domain_knowledge = {
            "software": ["modular design", "abstraction", "patterns", "refactoring"],
            "hardware": ["optimization", "efficiency", "resource management"],
            "business": ["process improvement", "automation", "streamlining"],
            "science": ["hypothesis", "experimentation", "analysis"],
        }

    def solve_creatively(
        self, problem: str, constraints: list[str] = None, context: dict[str, Any] = None
    ) -> list[Solution]:
        """
        Generate creative solutions to a problem
        Uses multiple creative techniques
        """
        import uuid

        constraints = constraints or []
        context = context or {}

        solutions = []

        # Technique 1: Divergent Thinking
        divergent_solutions = self._divergent_thinking(problem, constraints)
        solutions.extend(divergent_solutions)

        # Technique 2: Constraint Relaxation
        relaxed_solutions = self._constraint_relaxation(problem, constraints)
        solutions.extend(relaxed_solutions)

        # Technique 3: Cross-Domain Transfer
        cross_domain_solutions = self._cross_domain_transfer(problem, context)
        solutions.extend(cross_domain_solutions)

        # Technique 4: Combinatorial Synthesis
        combinatorial_solutions = self._combinatorial_synthesis(problem, solutions)
        solutions.extend(combinatorial_solutions)

        # Technique 5: Analogical Reasoning
        analogical_solutions = self._analogical_reasoning(problem)
        solutions.extend(analogical_solutions)

        # Technique 6: Reverse Thinking
        reverse_solutions = self._reverse_thinking(problem, constraints)
        solutions.extend(reverse_solutions)

        # Score and rank solutions
        scored_solutions = []
        for solution in solutions:
            solution.solution_id = str(uuid.uuid4())
            solution.combined_score = (
                solution.novelty_score * 0.6 + solution.feasibility_score * 0.4
            )
            scored_solutions.append(solution)

        # Sort by combined score
        scored_solutions.sort(key=lambda x: x.combined_score, reverse=True)

        self.solution_history.extend(scored_solutions)
        return scored_solutions[:10]  # Return top 10

    def _divergent_thinking(self, problem: str, constraints: list[str]) -> list[Solution]:
        """Generate many diverse solutions"""
        solutions = []

        # Extract problem components
        components = self._extract_problem_components(problem)

        # Generate variations
        for i in range(5):  # Generate 5 variations
            variation = self._generate_variation(components, i)
            novelty = 0.7 + random.uniform(0, 0.2)
            feasibility = 0.6 + random.uniform(0, 0.2)
            solution = Solution(
                solution_id="",
                description=variation,
                technique=CreativityTechnique.DIVERGENT_THINKING,
                novelty_score=novelty,
                feasibility_score=feasibility,
                combined_score=(novelty + feasibility) / 2.0,
            )
            solutions.append(solution)

        return solutions

    def _constraint_relaxation(self, problem: str, constraints: list[str]) -> list[Solution]:
        """Relax constraints to find solutions"""
        solutions = []

        if not constraints:
            return solutions

        # Identify constraint types
        relaxed_constraints = []
        for constraint in constraints:
            constraint_type = self._identify_constraint_type(constraint)
            relaxed = self._relax_constraint(constraint, constraint_type)
            if relaxed:
                relaxed_constraints.append(relaxed)

        # Generate solutions with relaxed constraints
        for relaxed in relaxed_constraints[:3]:  # Top 3 relaxed constraints
            solution_desc = f"Solution assuming {relaxed['relaxed_constraint']}: {problem}"
            solution = Solution(
                solution_id="",
                description=solution_desc,
                technique=CreativityTechnique.CONSTRAINT_RELAXATION,
                novelty_score=0.8,
                feasibility_score=0.7,
                combined_score=(0.8 + 0.7) / 2.0,
                constraints_relaxed=[relaxed["original"]],
            )
            solutions.append(solution)

        return solutions

    def _cross_domain_transfer(self, problem: str, context: dict[str, Any]) -> list[Solution]:
        """Transfer solutions from other domains"""
        solutions = []

        # Identify problem domain
        problem_domain = self._identify_domain(problem)

        # Find similar problems in other domains
        other_domains = [d for d in self.domain_knowledge if d != problem_domain]

        for other_domain in other_domains[:2]:  # Check 2 other domains
            domain_techniques = self.domain_knowledge.get(other_domain, [])

            for technique in domain_techniques[:2]:  # Use 2 techniques per domain
                transferred = self._transfer_technique(technique, problem_domain, other_domain)
                if transferred:
                    solution = Solution(
                        solution_id="",
                        description=transferred,
                        technique=CreativityTechnique.CROSS_DOMAIN_TRANSFER,
                        novelty_score=0.75,
                        feasibility_score=0.65,
                        combined_score=(0.75 + 0.65) / 2.0,
                        domains_combined=[problem_domain, other_domain],
                    )
                    solutions.append(solution)

        return solutions

    def _combinatorial_synthesis(
        self, problem: str, existing_solutions: list[Solution]
    ) -> list[Solution]:
        """Combine multiple solutions into new ones"""
        solutions = []

        if len(existing_solutions) < 2:
            return solutions

        # Combine pairs of solutions
        for i, sol1 in enumerate(existing_solutions[:3]):  # Limit combinations
            for sol2 in existing_solutions[i + 1 : min(i + 4, len(existing_solutions))]:
                combined = self._combine_solutions(sol1, sol2, problem)
                if combined:
                    solution = Solution(
                        solution_id="",
                        description=combined,
                        technique=CreativityTechnique.COMBINATORIAL_SYNTHESIS,
                        novelty_score=0.85,
                        feasibility_score=0.7,
                        combined_score=(0.85 + 0.7) / 2.0,
                        domains_combined=sol1.domains_combined + sol2.domains_combined,
                    )
                    solutions.append(solution)

        return solutions[:3]  # Limit to 3 combinations

    def _analogical_reasoning(self, problem: str) -> list[Solution]:
        """Use analogies to find solutions"""
        solutions = []

        # Find analogies
        problem_type = self._classify_problem_type(problem)
        analogies = self.analogy_database.get(problem_type, [])

        if not analogies:
            # Generate analogies
            analogies = self._generate_analogies(problem)

        for analogy in analogies[:3]:  # Use top 3 analogies
            analogy_text = analogy["analogy"]
            application_text = analogy["application"]
            solution_desc = (
                f"Solution inspired by analogy: {analogy_text}. " f"Applied: {application_text}"
            )
            solution = Solution(
                solution_id="",
                description=solution_desc,
                technique=CreativityTechnique.ANALOGICAL_REASONING,
                novelty_score=0.8,
                feasibility_score=0.7,
                combined_score=(0.8 + 0.7) / 2.0,
            )
            solutions.append(solution)

        return solutions

    def _reverse_thinking(self, problem: str, constraints: list[str]) -> list[Solution]:
        """Think in reverse - what would make the problem worse? Then invert"""
        solutions = []

        # Identify what would make problem worse
        worse_scenarios = self._generate_worse_scenarios(problem)

        # Invert to find solutions
        for worse in worse_scenarios[:2]:  # Top 2
            inverted = self._invert_scenario(worse)
            solution = Solution(
                solution_id="",
                description=f"Reverse thinking: {inverted}",
                technique=CreativityTechnique.REVERSE_THINKING,
                novelty_score=0.75,
                feasibility_score=0.7,
                combined_score=(0.75 + 0.7) / 2.0,
            )
            solutions.append(solution)

        return solutions

    def _extract_problem_components(self, problem: str) -> dict[str, Any]:
        """Extract components from problem"""
        return {
            "goal": self._extract_goal(problem),
            "obstacles": self._extract_obstacles(problem),
            "requirements": self._extract_requirements(problem),
            "context": problem,
        }

    def _generate_variation(self, components: dict[str, Any], variation_index: int) -> str:
        """Generate a variation of the solution"""
        goal = components["goal"]
        obstacle = components["obstacles"][0] if components["obstacles"] else "key challenges"
        variations = [
            f"Approach {variation_index + 1}: Focus on {goal} by addressing {obstacle}",
            f"Alternative {variation_index + 1}: Reimagine {goal} with different constraints",
            f"Variation {variation_index + 1}: Combine {goal} with innovative techniques",
        ]
        return variations[variation_index % len(variations)]

    def _identify_constraint_type(self, constraint: str) -> str:
        """Identify type of constraint"""
        constraint_lower = constraint.lower()
        for constraint_type, patterns in self.constraint_patterns.items():
            if any(pattern in constraint_lower for pattern in patterns):
                return constraint_type
        return "general"

    def _relax_constraint(self, constraint: str, constraint_type: str) -> dict[str, Any] | None:
        """Relax a constraint"""
        relaxations = {
            "resource": {
                "original": constraint,
                "relaxed_constraint": "Assume additional resources available",
            },
            "time": {"original": constraint, "relaxed_constraint": "Assume flexible timeline"},
            "technical": {
                "original": constraint,
                "relaxed_constraint": "Assume technical capability exists",
            },
            "cost": {"original": constraint, "relaxed_constraint": "Assume budget flexibility"},
        }
        return relaxations.get(constraint_type)

    def _identify_domain(self, problem: str) -> str:
        """Identify domain of problem"""
        problem_lower = problem.lower()
        for domain in self.domain_knowledge:
            if domain in problem_lower:
                return domain
        return "general"

    def _transfer_technique(
        self, technique: str, target_domain: str, source_domain: str
    ) -> str | None:
        """Transfer a technique from source to target domain"""
        return f"Apply {technique} from {source_domain} domain to solve {target_domain} problem"

    def _combine_solutions(self, sol1: Solution, sol2: Solution, problem: str) -> str | None:
        """Combine two solutions"""
        return (
            f"Hybrid approach: {sol1.description[:50]}... combined with {sol2.description[:50]}..."
        )

    def _classify_problem_type(self, problem: str) -> str:
        """Classify type of problem"""
        problem_lower = problem.lower()
        if "optimize" in problem_lower or "improve" in problem_lower:
            return "optimization"
        elif "fix" in problem_lower or "error" in problem_lower:
            return "fixing"
        elif "create" in problem_lower or "build" in problem_lower:
            return "creation"
        elif "analyze" in problem_lower or "understand" in problem_lower:
            return "analysis"
        return "general"

    def _generate_analogies(self, problem: str) -> list[dict[str, Any]]:
        """Generate analogies for problem"""
        problem_type = self._classify_problem_type(problem)

        analogies_db = {
            "optimization": [
                {
                    "analogy": "Like tuning a race car",
                    "application": "Fine-tune each component for peak performance",
                },
                {
                    "analogy": "Like organizing a library",
                    "application": "Systematically categorize and optimize",
                },
            ],
            "fixing": [
                {
                    "analogy": "Like debugging a circuit",
                    "application": "Trace the signal path to find the break",
                },
                {
                    "analogy": "Like solving a puzzle",
                    "application": "Identify missing pieces and fit them together",
                },
            ],
            "creation": [
                {
                    "analogy": "Like building a house",
                    "application": "Start with foundation, build up systematically",
                },
                {"analogy": "Like composing music", "application": "Combine elements harmoniously"},
            ],
        }

        return analogies_db.get(
            problem_type,
            [
                {
                    "analogy": "Like solving a complex problem",
                    "application": "Break it down systematically",
                }
            ],
        )

    def _generate_worse_scenarios(self, problem: str) -> list[str]:
        """Generate scenarios that would make problem worse"""
        return [
            f"Make {problem} more complex",
            f"Add more constraints to {problem}",
            f"Remove resources from solving {problem}",
        ]

    def _invert_scenario(self, worse_scenario: str) -> str:
        """Invert a worse scenario to find solution"""
        inversions = {
            "more complex": "simplify",
            "more constraints": "remove constraints",
            "remove resources": "add resources",
        }

        for key, value in inversions.items():
            if key in worse_scenario.lower():
                return worse_scenario.replace(key, value)

        return f"Opposite of: {worse_scenario}"

    def _extract_goal(self, problem: str) -> str:
        """Extract goal from problem"""
        # Look for goal indicators
        goal_patterns = [
            r"to\s+(\w+(?:\s+\w+)*)",
            r"goal\s+is\s+to\s+(\w+(?:\s+\w+)*)",
            r"want\s+to\s+(\w+(?:\s+\w+)*)",
        ]

        for pattern in goal_patterns:
            match = __import__("re").search(pattern, problem, __import__("re").IGNORECASE)
            if match:
                return match.group(1)

        return "solve the problem"

    def _extract_obstacles(self, problem: str) -> list[str]:
        """Extract obstacles from problem"""
        obstacles = []

        obstacle_patterns = [
            r"but\s+(\w+(?:\s+\w+)*)",
            r"however\s+(\w+(?:\s+\w+)*)",
            r"challenge\s+is\s+(\w+(?:\s+\w+)*)",
        ]

        for pattern in obstacle_patterns:
            matches = __import__("re").findall(pattern, problem, __import__("re").IGNORECASE)
            obstacles.extend(matches)

        return obstacles[:3]  # Limit to 3

    def _extract_requirements(self, problem: str) -> list[str]:
        """Extract requirements from problem"""
        requirements = []

        req_patterns = [
            r"must\s+(\w+(?:\s+\w+)*)",
            r"need\s+to\s+(\w+(?:\s+\w+)*)",
            r"require\s+(\w+(?:\s+\w+)*)",
        ]

        for pattern in req_patterns:
            matches = __import__("re").findall(pattern, problem, __import__("re").IGNORECASE)
            requirements.extend(matches)

        return requirements[:5]  # Limit to 5

    def get_best_solution(self, problem: str) -> Solution | None:
        """Get best solution for a problem"""
        solutions = self.solve_creatively(problem)
        return solutions[0] if solutions else None

    def get_solution_history(self) -> list[Solution]:
        """Get history of solutions"""
        return self.solution_history

    def get_status(self) -> dict[str, Any]:
        """Get solver status"""
        return {
            "solutions_generated": len(self.solution_history),
            "domains_covered": list(self.domain_knowledge.keys()),
            "techniques_available": [t.value for t in CreativityTechnique],
        }
