#!/usr/bin/env python3
"""
Aurora Terminal Client
Interactive terminal interface to Aurora with full capabilities

Requirements:
    pip install requests

Usage:
    python3 tools/aurora_terminal_client.py
    python3 tools/aurora_terminal_client.py --server http://127.0.0.1:5000
    python3 tools/aurora_terminal_client.py --message "Hello Aurora"
"""

import asyncio
import os
import sys
from datetime import datetime
import json
from pathlib import Path
from typing import Optional

try:
    import requests as requests_lib
    REQUESTS_AVAILABLE = True
except ImportError:
    requests_lib = None  # type: ignore
    REQUESTS_AVAILABLE = False


def _default_server_url() -> str:
    scheme = os.getenv("AURORA_SCHEME", "http")
    host = os.getenv("AURORA_HOST", "127.0.0.1")
    port = os.getenv("AURORA_PORT", "5000")
    return os.getenv("AURORA_SERVER_URL") or os.getenv("AURORA_BASE_URL") or f"{scheme}://{host}:{port}"


class AuroraTerminalClient:
    """Terminal client for Aurora"""

    def __init__(self, server_url: str | None = None):
        self.server_url = server_url or _default_server_url()
        self.session_id = f"terminal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.conversation_history = []
        self.config_file = Path.home() / ".aurora_terminal_config"
        self.load_config()

    def load_config(self):
        """Load terminal configuration"""
        if self.config_file.exists():
            try:
                self.config = json.loads(self.config_file.read_text())
            except Exception:
                self.config = self._default_config()
        else:
            self.config = self._default_config()
            self.save_config()

    def _default_config(self):
        return {
            "show_thinking": False,
            "use_color": True,
            "enable_clipboard": True
        }

    def save_config(self):
        """Save terminal configuration"""
        try:
            self.config_file.write_text(json.dumps(self.config, indent=2))
        except Exception:
            pass

    async def send_message(self, message: str) -> Optional[str]:
        """Send message to Aurora and get response with streaming support"""
        if not REQUESTS_AVAILABLE or requests_lib is None:
            return "Error: requests library not installed. Run: pip install requests"

        try:
            response = requests_lib.post(
                f"{self.server_url}/api/chat",
                json={
                    "message": message,
                    "session_id": self.session_id,
                    "client": "terminal"
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response") or data.get("message", "")

                if data.get("thinking"):
                    print(f"\n[Thinking: {data['thinking'][:100]}...]")

                return response_text
            elif response.status_code == 429:
                return "Rate limited. Please wait a moment and try again."
            elif response.status_code == 503:
                return "Aurora is temporarily unavailable. Please try again later."
            else:
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get(
                        "error") or error_data.get("message", error_msg)
                except Exception:
                    pass
                return f"Error ({response.status_code}): {error_msg}"
        except requests_lib.exceptions.ConnectionError:
            return "Cannot connect to Aurora server. Is it running? Try: npm run dev"
        except requests_lib.exceptions.Timeout:
            return "Request timed out. Aurora might be processing a complex request. Try again."
        except Exception as e:
            return f"Error: {str(e)}"

    def send_message_sync(self, message: str) -> Optional[str]:
        """Synchronous version of send_message for single-shot requests"""
        if not REQUESTS_AVAILABLE or requests_lib is None:
            return "Error: requests library not installed. Run: pip install requests"

        try:
            response = requests_lib.post(
                f"{self.server_url}/api/chat",
                json={
                    "message": message,
                    "session_id": self.session_id,
                    "client": "terminal"
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response") or data.get("message", "")
            else:
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get(
                        "error") or error_data.get("message", error_msg)
                except Exception:
                    pass
                return f"Error ({response.status_code}): {error_msg}"
        except requests_lib.exceptions.ConnectionError:
            return "Cannot connect to Aurora server. Is it running?"
        except Exception as e:
            return f"Error: {str(e)}"

    async def interactive_session(self):
        """Run interactive terminal session"""
        print("\n" + "=" * 60)
        print("           AURORA TERMINAL CLIENT")
        print("        Talk to Aurora from your terminal!")
        print("=" * 60 + "\n")

        print(f"Server: {self.server_url}")
        print(f"Session: {self.session_id}")
        print("Commands: type 'help' for commands, 'quit' to exit\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("\nAurora: Goodbye! Come back soon!\n")
                    break

                if user_input.lower() == "help":
                    self.show_help()
                    continue

                if user_input.lower() == "clear":
                    os.system("clear" if os.name != "nt" else "cls")
                    continue

                if user_input.lower() == "status":
                    await self.show_status()
                    continue

                if user_input.lower() == "history":
                    self.show_history()
                    continue

                if user_input.lower() == "config":
                    print(
                        f"\nConfiguration: {json.dumps(self.config, indent=2)}\n")
                    continue

                print("\nAurora: ", end="", flush=True)
                response = await self.send_message(user_input)
                print(response)
                print()

                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "aurora": response
                })

            except KeyboardInterrupt:
                print("\n\nAurora: Caught that interrupt! Take care!\n")
                break
            except EOFError:
                print("\n\nAurora: End of input. Goodbye!\n")
                break
            except Exception as e:
                print(f"\nError: {e}\n")

    async def show_status(self):
        """Show Aurora server status"""
        if requests_lib is None:
            print("\nStatus: Cannot check (requests library not installed)\n")
            return

        try:
            response = requests_lib.get(
                f"{self.server_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"\nServer Status: {data.get('status', 'unknown')}")
                print(f"Uptime: {data.get('uptime', 'unknown')} seconds")
                print(f"Service: {data.get('service', 'unknown')}\n")
            else:
                print(f"\nServer returned: {response.status_code}\n")
        except Exception as e:
            print(f"\nCannot reach server: {e}\n")

    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("\nNo conversation history yet.\n")
            return

        print("\n--- Conversation History ---")
        for entry in self.conversation_history[-10:]:
            print(f"\n[{entry['timestamp']}]")
            print(f"You: {entry['user']}")
            print(
                f"Aurora: {entry['aurora'][:200]}{'...' if len(entry['aurora']) > 200 else ''}")
        print("\n----------------------------\n")

    def show_help(self):
        """Show help for terminal commands"""
        print("""
================================================================
                    AURORA TERMINAL HELP
================================================================

Commands:
  help       - Show this help message
  clear      - Clear the screen
  status     - Show Aurora server status
  config     - Show current configuration
  history    - Show conversation history (last 10)
  quit       - Exit Aurora terminal

Tips:
  - Type normally to chat with Aurora
  - Type 'create file.py' to generate code
  - Type 'fix error' for debugging help
  - Use Ctrl+C to interrupt

================================================================
""")


def check_dependencies():
    """Check if required dependencies are installed"""
    if not REQUESTS_AVAILABLE:
        print("Error: 'requests' library is not installed.")
        print("Install it with: pip install requests")
        print("")
        print("Or run: pip install -r requirements.txt")
        sys.exit(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Aurora Terminal Client - Chat with Aurora from your terminal",
        epilog="Examples:\n"
               "  python3 tools/aurora_terminal_client.py\n"
               "  python3 tools/aurora_terminal_client.py --message 'Hello!'\n"
               "  python3 tools/aurora_terminal_client.py --server http://127.0.0.1:5000",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--server",
        default=_default_server_url(),
        help="Aurora server URL (default: $AURORA_SERVER_URL or $AURORA_BASE_URL)"
    )
    parser.add_argument(
        "--session",
        help="Existing session ID (for continuing conversations)"
    )
    parser.add_argument(
        "--message", "-m",
        help="Send a single message and exit"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check server status and exit"
    )

    args = parser.parse_args()

    check_dependencies()

    client = AuroraTerminalClient(server_url=args.server)

    if args.session:
        client.session_id = args.session

    if args.check:
        asyncio.run(client.show_status())
    elif args.message:
        response = client.send_message_sync(args.message)
        print(response)
    else:
        asyncio.run(client.interactive_session())


if __name__ == "__main__":
    main()
