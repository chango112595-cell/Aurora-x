#!/usr/bin/env python3
"""
Luminar Nexus - Memory Fabric Integration
------------------------------------------
Routes messages through Memory Fabric for persistent context.

Author: Aurora AI System
Version: 2.0-enhanced
"""

from core.memory_fabric import get_memory_fabric


class NexusMemoryBridge:
    """Bridge between Luminar Nexus and Memory Fabric"""

    def __init__(self):
        self.memory = get_memory_fabric(base="data/memory")
        self.memory.set_project("Luminar-Nexus")
        print("[Nexus Bridge] Memory Fabric connected")

    def route_to_core(self, message: str, user_id: str = "anonymous") -> dict:
        """Route incoming message through memory system"""
        self.memory.log_event(
            "incoming_message", {"user_id": user_id, "message_length": len(message)}
        )

        self.memory.save_message("user", message, tags=[user_id])

        context = self.memory.contextual_recall(message)

        return {
            "message": message,
            "context": context,
            "facts": self.memory.get_all_facts(),
            "stats": self.memory.get_stats(),
        }

    def store_response(self, response: str, metadata: dict = None) -> None:
        """Store Aurora's response in memory"""
        self.memory.save_message("aurora", response, tags=["response"], importance=0.7)
        self.memory.log_event("response_stored", metadata or {})


def route_to_core(message: str) -> dict:
    """Convenience function for routing messages"""
    bridge = NexusMemoryBridge()
    return bridge.route_to_core(message)


if __name__ == "__main__":
    bridge = NexusMemoryBridge()
    result = bridge.route_to_core("Hello Aurora, remember this conversation!")
    print("Route result:", result)
