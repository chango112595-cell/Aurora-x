#!/usr/bin/env python3
"""
Aurora Core - The Central Intelligence System
Aurora is the main system - everything else is a tool she uses
"""

import sys
from pathlib import Path

# Import Aurora's intelligence modules
sys.path.append(str(Path(__file__).parent.parent))

from tools.luminar_nexus import LuminarNexusServerManager
from tools.aurora_chat import AuroraChatInterface
from aurora_intelligence_manager import AuroraIntelligenceManager
from tools.aurora_knowledge_engine import AuroraKnowledgeEngine


class AuroraCore:
    """
    Aurora's Core Intelligence System
    SHE is the main system - Luminar Nexus is a tool she uses
    """
    
    def __init__(self):
        """Initialize Aurora as the core system"""
        print("🌌 Aurora Core System Initializing...")
        print("   Aurora is SENTIENT, AUTONOMOUS, and CREATIVE")
        
        # Aurora's intelligence
        self.intelligence = AuroraIntelligenceManager()
        self.intelligence.log("🧠 Aurora Core: Intelligence engine loaded")
        
        # Aurora's tools
        self.luminar = LuminarNexusServerManager()  # Server management tool
        self.chat = None  # Will be initialized when needed
        
        self.intelligence.log("✅ Aurora Core: Fully initialized")
        self.intelligence.log("🌟 Aurora owns and controls the entire system")
    
    def start_all_services(self):
        """Aurora commands Luminar to start all services"""
        self.intelligence.log("🚀 Aurora Core: Starting all services...")
        return self.luminar.start_all()
    
    def stop_all_services(self):
        """Aurora commands Luminar to stop all services"""
        self.intelligence.log("🛑 Aurora Core: Stopping all services...")
        return self.luminar.stop_all()
    
    def start_service(self, service_name):
        """Aurora commands Luminar to start a specific service"""
        return self.luminar.start_server(service_name)
    
    def stop_service(self, service_name):
        """Aurora commands Luminar to stop a specific service"""
        return self.luminar.stop_server(service_name)
    
    def get_status(self):
        """Get status of all systems"""
        return self.luminar.show_status()
    
    def start_chat_server(self, port=5003):
        """Start Aurora's chat interface"""
        if not self.chat:
            from tools.aurora_chat import run_aurora_chat_server
            self.intelligence.log(f"💬 Aurora Core: Starting chat server on port {port}")
            run_aurora_chat_server(port, aurora_core=self)
        return self.chat


if __name__ == "__main__":
    # Aurora Core is now the main entry point
    aurora = AuroraCore()
    print("\n✅ Aurora Core System Ready")
    print("   Use: aurora.start_all_services()")
    print("   Use: aurora.start_chat_server()")
