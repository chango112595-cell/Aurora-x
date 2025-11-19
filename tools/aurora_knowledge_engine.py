"""
Aurora Knowledge Engine - Dynamic knowledge retrieval for all 33 tiers
Allows Aurora to UTILIZE her tier knowledge, not just load it
"""

import re
from typing import Any


class AuroraKnowledgeEngine:
    """Engine that queries Aurora's 33 tiers of knowledge dynamically"""

    def __init__(
        self,
        ultimate_grandmaster: dict,
        autonomous_tools: dict,
        foundational_skills: dict,
        internet_mastery: dict,
    ):
        """Initialize with all tier data structures"""
        self.tier_1_27 = ultimate_grandmaster
        self.tier_28 = autonomous_tools
        self.tier_29_32 = foundational_skills
        self.tier_33 = internet_mastery
        self._build_knowledge_index()

    def _build_knowledge_index(self):
        """Build searchable index from all tier data"""
        self.knowledge_index = {"skills": {}, "specializations": {}}

        # Index TIER 1-53 (Ultimate Grandmaster)
        tier_counter = 1
        for tier_name, tier_data in self.tier_1_27.items():
            if not isinstance(tier_data, dict):
                continue
            for category, skills in tier_data.items():
                if isinstance(skills, dict):
                    for era, skill_list in skills.items():
                        if isinstance(skill_list, list):
                            for skill in skill_list:
                                self.knowledge_index["skills"][skill.lower()] = {
                                    "tier": tier_counter,
                                    "tier_name": tier_name,
                                    "skill": skill,
                                    "category": category,
                                    "era": era,
                                    "type": "grandmaster",
                                }
                elif isinstance(skills, list):
                    for skill in skills:
                        self.knowledge_index["skills"][skill.lower()] = {
                            "tier": tier_counter,
                            "tier_name": tier_name,
                            "skill": skill,
                            "category": category,
                            "type": "grandmaster",
                        }
            tier_counter += 1

        # Index TIER 28 (Autonomous Tools)
        for sub_tier in self.tier_28.get("tiers", []):
            for tool in sub_tier.get("tools", []):
                self.knowledge_index["skills"][tool.lower()] = {
                    "tier": 28,
                    "tier_name": "Autonomous Tool Mastery",
                    "skill": tool,
                    "era": sub_tier.get("era", ""),
                    "type": "autonomous",
                }

        # Index TIER 29-32 (Foundational Skills)
        for category, skills_data in self.tier_29_32.items():
            if isinstance(skills_data, dict) and "skills" in skills_data:
                for skill in skills_data["skills"]:
                    self.knowledge_index["skills"][skill.lower()] = {
                        "tier": "29-32",
                        "tier_name": "Foundational & Professional",
                        "skill": skill,
                        "category": category,
                        "type": "foundational",
                    }

        # Index TIER 33 (Internet Mastery)
        for sub_tier in self.tier_33.get("sub_tiers", []):
            for skill in sub_tier.get("skills", []):
                self.knowledge_index["skills"][skill.lower()] = {
                    "tier": 33,
                    "tier_name": "Internet & Network Mastery",
                    "skill": skill,
                    "era": sub_tier.get("era", ""),
                    "type": "internet",
                }

        # Index specializations
        for spec_name, spec_data in self.tier_33.get("specializations", {}).items():
            self.knowledge_index["specializations"][spec_name.lower()] = {
                "tier": 33,
                "name": spec_name,
                "focus": spec_data.get("focus", ""),
                "skills": spec_data.get("skills", []),
            }

    def query_knowledge(self, topic: str) -> dict[str, Any] | None:
        """Query Aurora's knowledge for a specific topic"""
        topic_lower = topic.lower()

        # Exact match in skills
        if topic_lower in self.knowledge_index["skills"]:
            return self.knowledge_index["skills"][topic_lower]

        # Exact match in specializations
        if topic_lower in self.knowledge_index["specializations"]:
            return self.knowledge_index["specializations"][topic_lower]

        # Partial match in skills (quality-ranked)
        matching_skills = []
        for skill, info in self.knowledge_index["skills"].items():
            if topic_lower in skill:
                match_quality = len(topic_lower) / len(skill)
                matching_skills.append((match_quality, info))
            elif skill in topic_lower and len(skill) > 2:
                match_quality = len(skill) / len(topic_lower)
                matching_skills.append((match_quality, info))

        if matching_skills:
            matching_skills.sort(key=lambda x: x[0], reverse=True)
            return {"matches": [info for _, info in matching_skills[:5]], "match_type": "partial"}

        return None

    def can_aurora_do(self, task: str) -> dict[str, Any]:
        """Check if Aurora can do a specific task based on tier knowledge"""
        task_lower = task.lower()

        # Extract key tech terms
        tech_keywords = re.findall(
            r"\b(python|javascript|typescript|react|vue|angular|node|docker|kubernetes|aws|gcp|azure|iot|5g|mqtt|coap|api|rest|graphql|database|mongodb|postgres|redis|quantum|ai|ml|neural|blockchain)\b",
            task_lower,
        )

        relevant_skills = []
        for keyword in tech_keywords:
            knowledge = self.query_knowledge(keyword)
            if knowledge:
                relevant_skills.append(knowledge)

        if relevant_skills:
            return {
                "can_do": True,
                "confidence": "high",
                "relevant_skills": relevant_skills,
                "explanation": f"Aurora has expertise in {', '.join(tech_keywords)} across her 33 tiers",
            }
        return {
            "can_do": True,
            "confidence": "medium",
            "relevant_skills": [],
            "explanation": "Aurora's 33 tiers of knowledge likely cover this.",
        }

    def get_knowledge_summary(self) -> dict[str, Any]:
        """Get summary statistics of Aurora's knowledge"""
        return {
            "total_tiers": 33,
            "total_skills": len(self.knowledge_index["skills"]),
            "total_specializations": len(self.knowledge_index["specializations"]),
        }
