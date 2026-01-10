"""
Aurora Advanced Reasoning Engine
Self-contained multi-step reasoning, causal inference, and logical deduction
No external APIs or AI models - completely autonomous
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ReasoningType(Enum):
    """Types of reasoning Aurora can perform"""

    CHAIN_OF_THOUGHT = "chain_of_thought"
    CAUSAL_INFERENCE = "causal_inference"
    DEDUCTIVE = "deductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    INDUCTIVE = "inductive"


@dataclass
class ReasoningStep:
    """A single step in a reasoning chain"""

    step_id: str
    reasoning_type: ReasoningType
    premise: str
    conclusion: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReasoningChain:
    """A complete reasoning chain"""

    chain_id: str
    problem: str
    steps: list[ReasoningStep] = field(default_factory=list)
    final_conclusion: str | None = None
    confidence: float = 0.0
    reasoning_type: ReasoningType = ReasoningType.CHAIN_OF_THOUGHT


class CausalGraph:
    """Self-contained causal graph for causal inference"""

    def __init__(self):
        self.nodes: dict[str, dict[str, Any]] = {}
        self.edges: dict[str, list[tuple[str, float]]] = {}  # node -> [(target, strength)]

    def add_node(self, node_id: str, properties: dict[str, Any]):
        """Add a node to the causal graph"""
        self.nodes[node_id] = properties
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_causal_link(self, cause: str, effect: str, strength: float = 1.0):
        """Add a causal link between nodes"""
        if cause not in self.edges:
            self.edges[cause] = []
        self.edges[cause].append((effect, strength))

    def find_causal_paths(self, start: str, end: str, max_depth: int = 5) -> list[list[str]]:
        """Find all causal paths from start to end"""
        paths = []

        def dfs(current: str, path: list[str], visited: set[str]):
            if current == end:
                paths.append(path[:])
                return

            if len(path) >= max_depth or current in visited:
                return

            visited.add(current)
            for target, _ in self.edges.get(current, []):
                if target not in visited:
                    path.append(target)
                    dfs(target, path, visited)
                    path.pop()
            visited.remove(current)

        dfs(start, [start], set())
        return paths


class AdvancedReasoningEngine:
    """
    Self-contained advanced reasoning engine
    No external APIs - uses pattern matching, graph algorithms, and logical rules
    """

    def __init__(self):
        self.reasoning_chains: list[ReasoningChain] = []
        self.causal_graphs: dict[str, CausalGraph] = {}
        self.knowledge_base: dict[str, list[str]] = {}  # concept -> [related concepts]
        self.pattern_library: dict[str, list[str]] = {}  # pattern_type -> [patterns]
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize reasoning patterns"""
        self.pattern_library = {
            "causal": [
                r"if\s+(\w+)\s+then\s+(\w+)",
                r"(\w+)\s+causes\s+(\w+)",
                r"(\w+)\s+leads\s+to\s+(\w+)",
                r"(\w+)\s+results\s+in\s+(\w+)",
            ],
            "logical": [
                r"if\s+(\w+)\s+and\s+(\w+)\s+then\s+(\w+)",
                r"(\w+)\s+implies\s+(\w+)",
                r"(\w+)\s+requires\s+(\w+)",
                r"(\w+)\s+depends\s+on\s+(\w+)",
            ],
            "analogical": [
                r"(\w+)\s+is\s+like\s+(\w+)",
                r"(\w+)\s+similar\s+to\s+(\w+)",
                r"(\w+)\s+analogous\s+to\s+(\w+)",
            ],
        }

    def chain_of_thought_reasoning(
        self, problem: str, context: dict[str, Any] = None
    ) -> ReasoningChain:
        """
        Perform chain-of-thought reasoning
        Breaks down problem into steps and reasons through each
        """
        import uuid

        chain_id = str(uuid.uuid4())
        chain = ReasoningChain(chain_id=chain_id, problem=problem)
        context = context or {}

        # Step 1: Problem decomposition
        sub_problems = self._decompose_problem(problem)
        step1 = ReasoningStep(
            step_id=f"{chain_id}-step-1",
            reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
            premise=problem,
            conclusion=f"Problem decomposed into {len(sub_problems)} sub-problems",
            confidence=0.9,
            evidence=sub_problems,
        )
        chain.steps.append(step1)

        # Step 2: Analyze each sub-problem
        solutions = []
        for i, sub_problem in enumerate(sub_problems):
            analysis = self._analyze_sub_problem(sub_problem, context)
            step = ReasoningStep(
                step_id=f"{chain_id}-step-{i+2}",
                reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
                premise=sub_problem,
                conclusion=analysis["conclusion"],
                confidence=analysis["confidence"],
                evidence=analysis["evidence"],
                dependencies=[step1.step_id],
            )
            chain.steps.append(step)
            solutions.append(analysis)

        # Step 3: Synthesize solution
        final_solution = self._synthesize_solution(solutions, problem)
        chain.final_conclusion = final_solution["conclusion"]
        chain.confidence = final_solution["confidence"]

        self.reasoning_chains.append(chain)
        return chain

    def causal_inference(self, event: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """
        Perform causal inference to find causes of an event
        """
        context = context or {}

        # Build or retrieve causal graph
        graph_id = context.get("domain", "general")
        if graph_id not in self.causal_graphs:
            self.causal_graphs[graph_id] = CausalGraph()

        graph = self.causal_graphs[graph_id]

        # Extract entities from event
        entities = self._extract_entities(event)

        # Find potential causes
        potential_causes = []
        for entity in entities:
            # Look for patterns that suggest causes
            causes = self._find_potential_causes(entity, graph, context)
            potential_causes.extend(causes)

        # Rank causes by likelihood
        ranked_causes = self._rank_causes(potential_causes, event, context)

        return {
            "event": event,
            "potential_causes": ranked_causes[:5],  # Top 5
            "confidence": ranked_causes[0]["confidence"] if ranked_causes else 0.0,
            "reasoning": self._generate_causal_explanation(ranked_causes[:3]),
        }

    def deductive_reasoning(
        self, premises: list[str], conclusion_hypothesis: str = None
    ) -> dict[str, Any]:
        """
        Perform deductive reasoning from premises
        """
        # Extract logical structure
        logical_structure = self._extract_logical_structure(premises)

        # Apply logical rules
        derived_conclusions = self._apply_logical_rules(logical_structure)

        # If hypothesis provided, check if it follows
        if conclusion_hypothesis:
            follows = self._check_logical_consequence(derived_conclusions, conclusion_hypothesis)
            return {
                "premises": premises,
                "hypothesis": conclusion_hypothesis,
                "follows": follows,
                "derived_conclusions": derived_conclusions,
                "confidence": 0.9 if follows else 0.3,
            }

        return {
            "premises": premises,
            "derived_conclusions": derived_conclusions,
            "confidence": 0.8,
        }

    def abductive_reasoning(
        self, observation: str, possible_explanations: list[str] = None
    ) -> dict[str, Any]:
        """
        Perform abductive reasoning - find best explanation for observation
        """
        if not possible_explanations:
            possible_explanations = self._generate_explanations(observation)

        # Score each explanation
        scored_explanations = []
        for explanation in possible_explanations:
            score = self._score_explanation(explanation, observation)
            scored_explanations.append(
                {
                    "explanation": explanation,
                    "score": score,
                    "confidence": min(score / 100.0, 1.0),
                }
            )

        # Sort by score
        scored_explanations.sort(key=lambda x: x["score"], reverse=True)

        return {
            "observation": observation,
            "best_explanation": scored_explanations[0] if scored_explanations else None,
            "all_explanations": scored_explanations,
        }

    def analogical_reasoning(self, source_domain: str, target_domain: str) -> dict[str, Any]:
        """
        Perform analogical reasoning - transfer knowledge from source to target
        """
        # Extract structure from source
        source_structure = self._extract_domain_structure(source_domain)

        # Find mappings to target
        mappings = self._find_analogical_mappings(source_structure, target_domain)

        # Transfer knowledge
        transferred_knowledge = self._transfer_knowledge(source_structure, mappings, target_domain)

        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "mappings": mappings,
            "transferred_knowledge": transferred_knowledge,
            "confidence": self._calculate_analogy_confidence(mappings),
        }

    def _decompose_problem(self, problem: str) -> list[str]:
        """Decompose a problem into sub-problems"""
        # Use pattern matching to identify sub-problems
        sub_problems = []

        # Look for conjunctions (and, also, plus)
        parts = re.split(r"\s+(and|also|plus|,)\s+", problem, flags=re.IGNORECASE)
        if len(parts) > 1:
            sub_problems.extend(
                [
                    p.strip()
                    for p in parts
                    if p.strip() and p.lower() not in ["and", "also", "plus", ","]
                ]
            )
        else:
            # Look for sequential steps
            steps = re.split(r"\s+(then|next|after|followed by)\s+", problem, flags=re.IGNORECASE)
            if len(steps) > 1:
                sub_problems.extend(
                    [
                        s.strip()
                        for s in steps
                        if s.strip() and s.lower() not in ["then", "next", "after", "followed by"]
                    ]
                )
            else:
                # Single problem
                sub_problems = [problem]

        return sub_problems if sub_problems else [problem]

    def _analyze_sub_problem(self, sub_problem: str, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze a sub-problem"""
        # Extract key concepts
        concepts = self._extract_concepts(sub_problem)

        # Find related knowledge
        related_knowledge = []
        for concept in concepts:
            if concept in self.knowledge_base:
                related_knowledge.extend(self.knowledge_base[concept])

        # Generate analysis
        analysis = {
            "conclusion": f"Analysis of '{sub_problem}' reveals {len(concepts)} key concepts",
            "confidence": 0.7,
            "evidence": related_knowledge[:5] if related_knowledge else concepts,
        }

        return analysis

    def _synthesize_solution(
        self, solutions: list[dict[str, Any]], original_problem: str
    ) -> dict[str, Any]:
        """Synthesize solutions into final answer"""
        # Combine solutions
        combined_evidence = []
        total_confidence = 0.0

        for solution in solutions:
            combined_evidence.extend(solution.get("evidence", []))
            total_confidence += solution.get("confidence", 0.0)

        avg_confidence = total_confidence / len(solutions) if solutions else 0.0

        insights = ", ".join(combined_evidence[:3])
        conclusion = (
            f"Solution synthesized from {len(solutions)} sub-solutions. "
            f"Key insights: {insights}"
        )

        return {
            "conclusion": conclusion,
            "confidence": avg_confidence,
            "evidence": combined_evidence,
        }

    def _extract_entities(self, text: str) -> list[str]:
        """Extract entities from text"""
        # Simple entity extraction using patterns
        entities = []

        # Capitalized words (potential proper nouns)
        entities.extend(re.findall(r"\b[A-Z][a-z]+\b", text))

        # Quoted strings
        entities.extend(re.findall(r'"([^"]+)"', text))

        # Technical terms (words with underscores or camelCase)
        entities.extend(re.findall(r"\b[a-z]+_[a-z_]+\b", text))
        entities.extend(re.findall(r"\b[a-z]+[A-Z][a-zA-Z]+\b", text))

        return list(set(entities))

    def _find_potential_causes(
        self, entity: str, graph: CausalGraph, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Find potential causes for an entity"""
        causes = []

        # Check causal graph
        for node, edges in graph.edges.items():
            for target, strength in edges:
                if target == entity or entity.lower() in target.lower():
                    causes.append(
                        {
                            "cause": node,
                            "effect": target,
                            "strength": strength,
                            "source": "causal_graph",
                        }
                    )

        # Use pattern matching
        for _pattern_type, patterns in self.pattern_library.get("causal", []):
            for pattern in patterns:
                matches = re.findall(pattern, context.get("text", ""), re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple) and entity.lower() in str(match[1]).lower():
                        causes.append(
                            {
                                "cause": match[0],
                                "effect": match[1],
                                "strength": 0.7,
                                "source": "pattern",
                            }
                        )

        return causes

    def _rank_causes(
        self, causes: list[dict[str, Any]], event: str, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Rank causes by likelihood"""
        # Score each cause
        scored = []
        for cause in causes:
            score = cause.get("strength", 0.5) * 100

            # Boost score if cause appears in context
            context_text = context.get("text", "")
            if context_text and cause["cause"].lower() in context_text.lower():
                score += 20

            scored.append({**cause, "confidence": min(score / 100.0, 1.0)})

        # Sort by confidence
        scored.sort(key=lambda x: x["confidence"], reverse=True)
        return scored

    def _generate_causal_explanation(self, top_causes: list[dict[str, Any]]) -> str:
        """Generate explanation for causal inference"""
        if not top_causes:
            return "No clear causes identified."

        explanations = []
        for cause in top_causes:
            explanations.append(
                f"{cause['cause']} → {cause['effect']} (confidence: {cause['confidence']:.2f})"
            )

        return "Potential causal chain: " + " → ".join(explanations)

    def _extract_logical_structure(self, premises: list[str]) -> dict[str, Any]:
        """Extract logical structure from premises"""
        structure = {
            "premises": premises,
            "operators": [],
            "entities": [],
        }

        for premise in premises:
            # Extract logical operators
            if "and" in premise.lower():
                structure["operators"].append("AND")
            if "or" in premise.lower():
                structure["operators"].append("OR")
            if "not" in premise.lower() or "no" in premise.lower():
                structure["operators"].append("NOT")
            if "if" in premise.lower() and "then" in premise.lower():
                structure["operators"].append("IMPLIES")

            # Extract entities
            structure["entities"].extend(self._extract_entities(premise))

        return structure

    def _apply_logical_rules(self, structure: dict[str, Any]) -> list[str]:
        """Apply logical rules to derive conclusions"""
        conclusions = []

        # Modus ponens: If P then Q, P, therefore Q
        # Modus tollens: If P then Q, not Q, therefore not P
        # etc.

        premises = structure["premises"]
        operators = structure["operators"]

        if "IMPLIES" in operators:
            # Find implications
            for premise in premises:
                if "if" in premise.lower() and "then" in premise.lower():
                    # Extract P and Q
                    match = re.search(r"if\s+(.+?)\s+then\s+(.+?)(?:\.|$)", premise, re.IGNORECASE)
                    if match:
                        p = match.group(1).strip()
                        q = match.group(2).strip()

                        # Check if P is in other premises
                        for other_premise in premises:
                            if p.lower() in other_premise.lower() and premise != other_premise:
                                conclusions.append(f"Therefore: {q}")

        return conclusions

    def _check_logical_consequence(self, derived: list[str], hypothesis: str) -> bool:
        """Check if hypothesis logically follows from derived conclusions"""
        hypothesis.lower()

        for conclusion in derived:
            conclusion.lower()
            # Simple check: if hypothesis concepts appear in conclusion
            hypothesis_concepts = set(self._extract_concepts(hypothesis))
            conclusion_concepts = set(self._extract_concepts(conclusion))

            if hypothesis_concepts.issubset(conclusion_concepts):
                return True

        return False

    def _generate_explanations(self, observation: str) -> list[str]:
        """Generate possible explanations for an observation"""
        explanations = []

        # Extract key concepts
        concepts = self._extract_concepts(observation)

        # Generate explanations based on patterns
        for concept in concepts:
            explanations.append(f"{concept} may have caused this")
            explanations.append(f"External factor affecting {concept}")
            explanations.append(f"System state change in {concept}")

        return explanations[:5]  # Limit to 5

    def _score_explanation(self, explanation: str, observation: str) -> float:
        """Score an explanation's fit to observation"""
        score = 50.0  # Base score

        # Check concept overlap
        obs_concepts = set(self._extract_concepts(observation))
        exp_concepts = set(self._extract_concepts(explanation))

        overlap = len(obs_concepts & exp_concepts)
        score += overlap * 10

        # Check for causal language
        if any(word in explanation.lower() for word in ["cause", "lead", "result", "because"]):
            score += 20

        return min(score, 100.0)

    def _extract_domain_structure(self, domain: str) -> dict[str, Any]:
        """Extract structural elements from a domain"""
        concepts = self._extract_concepts(domain)
        relationships = []

        # Find relationships
        if "has" in domain.lower():
            relationships.append("has_relationship")
        if "uses" in domain.lower():
            relationships.append("uses_relationship")
        if "contains" in domain.lower():
            relationships.append("contains_relationship")

        return {
            "concepts": concepts,
            "relationships": relationships,
            "domain": domain,
        }

    def _find_analogical_mappings(
        self, source_structure: dict[str, Any], target_domain: str
    ) -> list[dict[str, Any]]:
        """Find mappings between source and target domains"""
        target_concepts = self._extract_concepts(target_domain)
        mappings = []

        # Simple mapping: match concepts by similarity
        for source_concept in source_structure["concepts"]:
            for target_concept in target_concepts:
                # Simple similarity check
                if (
                    source_concept.lower() in target_concept.lower()
                    or target_concept.lower() in source_concept.lower()
                ):
                    mappings.append(
                        {
                            "source": source_concept,
                            "target": target_concept,
                            "similarity": 0.8,
                        }
                    )

        return mappings

    def _transfer_knowledge(
        self, source_structure: dict[str, Any], mappings: list[dict[str, Any]], target_domain: str
    ) -> list[str]:
        """Transfer knowledge using mappings"""
        transferred = []

        for mapping in mappings:
            transferred.append(f"{mapping['source']} → {mapping['target']}")

        return transferred

    def _calculate_analogy_confidence(self, mappings: list[dict[str, Any]]) -> float:
        """Calculate confidence in analogy"""
        if not mappings:
            return 0.0

        avg_similarity = sum(m["similarity"] for m in mappings) / len(mappings)
        return avg_similarity

    def _extract_concepts(self, text: str) -> list[str]:
        """Extract key concepts from text"""
        # Extract nouns and important terms
        concepts = []

        # Words that are likely concepts (nouns, technical terms)
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text)

        # Filter out common words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
        }
        concepts = [w for w in words if w.lower() not in stop_words]

        return list(set(concepts))[:10]  # Limit to 10 unique concepts

    def get_reasoning_history(self) -> list[ReasoningChain]:
        """Get history of reasoning chains"""
        return self.reasoning_chains

    def get_status(self) -> dict[str, Any]:
        """Get engine status"""
        return {
            "reasoning_chains_count": len(self.reasoning_chains),
            "causal_graphs_count": len(self.causal_graphs),
            "knowledge_base_size": sum(len(v) for v in self.knowledge_base.values()),
            "pattern_types": list(self.pattern_library.keys()),
        }
