#!/usr/bin/env python3
"""
Aurora Core Intelligence - Memory Fabric Integration
-----------------------------------------------------
Integrates Aurora Memory Fabric v2 with Aurora Core Intelligence System.

Author: Aurora AI System
Version: 2.0-enhanced
"""

from core.memory_fabric import AuroraMemoryFabric, get_memory_fabric


class AuroraCoreIntelligence:
    """
    Aurora Core Intelligence with Memory Fabric Integration
    --------------------------------------------------------
    Enhanced with multi-tier hybrid memory system for:
    - Persistent fact storage
    - Conversation tracking
    - Semantic recall
    - Event logging
    """
    
    def __init__(self, project_name: str = "Aurora-X"):
        self.memory = get_memory_fabric(base="data/memory")
        self.memory.set_project(project_name)
        self.memory.log_event("core_initialized", {"project": project_name})
        print(f"[Aurora Core] Initialized with Memory Fabric for project: {project_name}")
    
    def process(self, user_input: str) -> str:
        """Process user input with memory integration"""
        self.memory.save_message("user", user_input)
        
        context = self.memory.contextual_recall(user_input)
        response = self.generate_response(user_input, context)
        
        self.memory.save_message("aurora", response)
        self.memory.log_event("response_generated", {
            "input_length": len(user_input),
            "response_length": len(response)
        })
        
        return response
    
    def generate_response(self, user_input: str, context: str = "") -> str:
        """Generate a response (placeholder for actual AI generation)"""
        if context:
            return f"Based on my memory ({context}), I understand your request."
        return "I've processed your input and will remember this conversation."
    
    def remember(self, key: str, value: str) -> None:
        """Store a fact in memory"""
        self.memory.remember_fact(key, value)
    
    def recall(self, key: str) -> str:
        """Recall a fact from memory"""
        return self.memory.recall_fact(key) or "I don't remember that."
    
    def get_context(self) -> str:
        """Get current context summary"""
        return self.memory.get_context_summary()
    
    def search_memory(self, query: str) -> list:
        """Semantic search through memory"""
        return self.memory.recall_semantic(query)


if __name__ == "__main__":
    core = AuroraCoreIntelligence("TestProject")
    core.remember("user_name", "Kai")
    print("Response:", core.process("What is my name?"))
    print("Recall:", core.recall("user_name"))