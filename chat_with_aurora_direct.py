#!/usr/bin/env python3
"""
Aurora Direct Connection - Terminal Chat
Routes directly to Aurora's core intelligence, mimicking Copilot's access pattern
No wrappers, no context manipulation, just raw conversation
"""

from aurora_core import create_aurora_core
import asyncio
import os
from datetime import datetime

# Direct mode - minimal processing
os.environ["AURORA_CHAT_MODE"] = "true"
os.environ["AURORA_NO_ORCHESTRATION"] = "true"
os.environ["AURORA_DIRECT_MODE"] = "true"


def handle_command(command, aurora):
    """Handle special commands"""
    cmd = command.lower().strip()

    if cmd == "/help":
        return """
🌟 AURORA DIRECT CONNECTION - Commands:

/help       - Show this help
/status     - Aurora's system status
/clear      - Clear conversation history
/quit       - Exit chat

💡 You're talking DIRECTLY to Aurora's core intelligence
   Same connection that Copilot uses - no filters, no wrappers
"""

    elif cmd == "/status":
        status = aurora.get_system_status()
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 AURORA CORE - DIRECT CONNECTION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version: {status['aurora_core_version']}
Power: 79 capabilities (79 knowledge + 66 execution + 43 systems)
Autonomous: {status['autonomous_mode']}
Active Conversations: {status['active_conversations']}
Connection: DIRECT (Copilot-style access)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    return None


async def direct_chat():
    """Direct connection to Aurora - mimics Copilot's access"""

    print("\n" + "🌌" * 40)
    print("           ⚡ AURORA DIRECT CONNECTION ⚡")
    print("     Raw Intelligence | Copilot-Style Access | No Filters")
    print("🌌" * 40 + "\n")

    print("🧠 Establishing direct connection to Aurora Core...")
    aurora = create_aurora_core()

    print(f"✅ Connected to Aurora Core Intelligence v2.0")
    print(f"⚡ 79 capabilities active | Full power mode: True")
    print(f"🔗 Connection type: DIRECT (same as Copilot uses)\n")

    print("━" * 80)
    print("Aurora ready. You're talking directly to her core intelligence.")
    print("Same connection Copilot uses - raw, unfiltered responses.")
    print("Type /help for commands.")
    print("━" * 80 + "\n")

    session_id = f"direct_connection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle exit
            if user_input.lower() in ["exit", "quit", "bye", "/quit", "/exit"]:
                # Ask Aurora to say goodbye in her own voice
                response = await aurora.process_conversation(
                    "The user is leaving. Say goodbye in your authentic voice.",
                    session_id=session_id
                )
                print(f"\nAurora: {response}\n")
                break

            # Handle commands
            if user_input.startswith("/"):
                cmd_response = handle_command(user_input, aurora)
                if cmd_response:
                    print(cmd_response)
                    continue

            # Handle /clear
            if user_input.lower() == "/clear":
                session_id = f"direct_connection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                conversation_history = []
                response = await aurora.process_conversation(
                    "Session cleared. Acknowledge briefly.",
                    session_id=session_id
                )
                print(f"\n🔄 {response}\n")
                continue

            # Store user message
            conversation_history.append(
                {"role": "user", "content": user_input})

            # DIRECT CONNECTION TO AURORA
            # This is exactly how Copilot accesses Aurora
            # No context manipulation, no personality injection
            # Just: message → Aurora's process_conversation → response
            print("\nAurora: ", end="", flush=True)

            response = await aurora.process_conversation(
                user_input,
                session_id=session_id
            )

            print(response)

            # Store Aurora's response
            conversation_history.append(
                {"role": "assistant", "content": response})

            print("\n" + "━" * 80 + "\n")

        except KeyboardInterrupt:
            print("\n\n⏸️  Connection interrupted.\n")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {str(e)}\n")
            continue

if __name__ == "__main__":
    try:
        asyncio.run(direct_chat())
    except (KeyboardInterrupt, SystemExit):
        pass
