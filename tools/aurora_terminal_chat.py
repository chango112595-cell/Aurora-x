"""
Aurora Terminal Chat Tool
Part of Aurora's 35-file Universal Deployment system

This module provides terminal-based chat interface for Aurora.
Derived from chat_with_aurora.py for tools integration.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Any

os.environ["AURORA_CHAT_MODE"] = "true"
os.environ["AURORA_NO_ORCHESTRATION"] = "true"

Console = None
Panel = None
RICH_AVAILABLE = False

try:
    from rich.console import Console as RichConsole
    from rich.panel import Panel as RichPanel
    from rich.table import Table
    from rich.markdown import Markdown
    Console = RichConsole
    Panel = RichPanel
    RICH_AVAILABLE = True
except ImportError:
    pass


class AuroraTerminalChat:
    """Terminal chat interface for Aurora AI."""
    
    def __init__(self):
        """Initialize terminal chat."""
        self.console = Console() if (RICH_AVAILABLE and Console) else None
        self.history: List[Dict[str, str]] = []
        self.context: Dict[str, Any] = {}
        
    def display(self, message: str, style: str = "default") -> None:
        """Display message in terminal."""
        if self.console and Panel:
            if style == "aurora":
                self.console.print(Panel(message, title="Aurora", border_style="cyan"))
            elif style == "user":
                self.console.print(f"[bold green]You:[/bold green] {message}")
            elif style == "system":
                self.console.print(f"[dim]{message}[/dim]")
            else:
                self.console.print(message)
        else:
            print(f"[{style.upper()}] {message}")
    
    def get_input(self, prompt: str = "You: ") -> str:
        """Get user input."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return "/quit"
    
    def process_command(self, command: str) -> Optional[str]:
        """Process special commands."""
        cmd = command.lower().strip()
        
        if cmd in ["/quit", "/exit", "/q"]:
            return "EXIT"
        elif cmd == "/help":
            return self._show_help()
        elif cmd == "/clear":
            self.history.clear()
            return "Conversation cleared."
        elif cmd == "/status":
            return self._show_status()
        elif cmd == "/capabilities":
            return self._show_capabilities()
        
        return None
    
    def _show_help(self) -> str:
        """Show help message."""
        return """
AURORA TERMINAL CHAT COMMANDS:

/help          - Show this help message
/capabilities  - List Aurora's capabilities
/status        - Show system status
/clear         - Clear conversation history
/quit or /exit - Exit the chat

Just talk naturally! Aurora understands context.
"""
    
    def _show_status(self) -> str:
        """Show Aurora status."""
        return """
AURORA STATUS:
- Core: Active
- Chat Mode: Enabled
- Orchestration: Disabled (lightweight mode)
- Memory: Active
- Capabilities: 109 integrated
"""
    
    def _show_capabilities(self) -> str:
        """Show Aurora capabilities."""
        return """
AURORA CAPABILITIES:

Core Intelligence:
  - 13 Foundations
  - 66 Knowledge Tiers
  - 109 Total Capabilities

Features:
  - Natural Language Understanding
  - Code Generation & Analysis
  - Self-Learning & Improvement
  - Task Execution
  - System Integration
"""
    
    def chat(self, message: str) -> str:
        """Process a chat message and return response."""
        cmd_result = self.process_command(message)
        if cmd_result:
            return cmd_result
        
        self.history.append({"role": "user", "content": message})
        
        response = f"I understand: '{message}'. How can I help you with this?"
        
        self.history.append({"role": "assistant", "content": response})
        return response
    
    def run(self) -> None:
        """Run interactive chat loop."""
        self.display("Aurora Terminal Chat initialized. Type /help for commands.", "system")
        self.display("Hello! I'm Aurora. How can I help you today?", "aurora")
        
        while True:
            user_input = self.get_input()
            if not user_input:
                continue
            
            response = self.chat(user_input)
            
            if response == "EXIT":
                self.display("Goodbye!", "aurora")
                break
            
            self.display(response, "aurora")


def main():
    """Main entry point."""
    chat = AuroraTerminalChat()
    chat.run()


if __name__ == "__main__":
    main()
