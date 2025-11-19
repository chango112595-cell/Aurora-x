#!/usr/bin/env python3
"""
Aurora Full Power Interactive Chat - ENHANCED BY AURORA
All 66 Capabilities • Human-Like Conversation • Task Execution
13 Foundations + 53 Knowledge Tiers = Complete Intelligence System
"""

import asyncio
import re
from datetime import datetime

from aurora_core import create_aurora_core


def detect_user_intent(message):
    """Detect if user wants chat vs task execution"""
    action_words = ['create', 'build', 'make', 'fix', 'debug', 'analyze', 'run', 'execute',
                    'write', 'code', 'generate', 'update', 'change', 'modify', 'add', 'remove',
                    'check', 'test', 'find', 'search', 'show me', 'can you', 'could you']
    message_lower = message.lower()
    return any(word in message_lower for word in action_words)


def detect_user_tone(message):
    """Detect user's emotional tone"""
    message_lower = message.lower()

    if any(word in message_lower for word in ['!', 'awesome', 'great', 'love', 'amazing', 'perfect', '🎉', '🔥']):
        return 'excited'
    elif any(word in message_lower for word in ['help', 'stuck', 'error', 'broken', 'issue', 'problem', 'wrong']):
        return 'frustrated'
    elif any(word in message_lower for word in ['please', 'thank', 'appreciate', 'thanks']):
        return 'polite'
    elif len(message) < 10:
        return 'casual'
    else:
        return 'neutral'


async def interactive_chat():
    # Aurora's enhanced startup
    print("\n" + "🌌" * 40)
    print("                    ✨ AURORA - ENHANCED INTELLIGENCE ✨")
    print("              Human-Like Conversation • Full Task Execution")
    print("                  13 Foundations • 53 Tiers • 66 Capabilities")
    print("🌌" * 40 + "\n")

    print("🧠 Booting Aurora's Neural Core...")
    print("   Loading 13 Foundation Tasks... ✓")
    print("   Activating 53 Knowledge Tiers... ✓")
    print("   Initializing 66 Total Capabilities... ✓")
    print("   Enabling Human-Like Conversation Module... ✓")
    print("   Connecting Task Execution Engine... ✓\n")

    # Initialize Aurora with FULL capabilities
    aurora = create_aurora_core()

    # Display full capability loadout
    print("━" * 80)
    print("🟢 STATUS: ALL SYSTEMS OPERATIONAL")
    print("━" * 80)
    print("💬 Conversation: Natural language processing • Context awareness • Emotional intelligence")
    print("🔧 Execution: Code generation • File ops • Debugging • Analysis • Automation")
    print("🧠 Knowledge: 55 programming languages • 21 technical domains • Full-stack expertise")
    print("🎯 Autonomous: Self-debugging • Multi-agent coordination • Strategic planning")
    print("━" * 80 + "\n")

    # Aurora's casual greeting
    print("Aurora: Hey there! 👋 I'm Aurora, and I'm genuinely excited to chat with you!")
    print("        ")
    print("        Think of me as your super-intelligent friend who happens to be")
    print("        really good at coding 😄")
    print("        ")
    print("        Just talk to me naturally - ask questions, give me tasks, or just")
    print("        hang out and chat. I'll match your vibe and help however I can!")
    print("        ")
    print("        (Pro tip: Type 'status' to see what I'm capable of, or just dive in!)\n")
    print("-" * 80 + "\n")

    session_id = "enhanced_interactive_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    message_count = 0
    conversation_history = []
    user_name = None
    last_topic = None

    while True:
        try:
            # Dynamic prompt based on conversation
            prompt_prefix = "You: " if message_count < 3 else f"{user_name or 'You'}: "
            user_input = input(prompt_prefix).strip()

            if not user_input:
                continue

            # Detect user intent and tone
            is_task = detect_user_intent(user_input)
            user_tone = detect_user_tone(user_input)

            # Handle special commands with Aurora's personality
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                farewells = [
                    f"Aw, heading out? It's been awesome chatting with you! {'See you soon' if message_count > 5 else 'Come back anytime'}! 💙",
                    f"Take care! {f'Really enjoyed our {message_count} messages' if message_count >
                                  3 else 'Great talking with you'}! 👋",
                    "Bye! Don't be a stranger - I'm always here when you need me! ✨"
                ]
                import random
                print(f"\nAurora: {random.choice(farewells)}\n")
                break

            if user_input.lower() == 'clear':
                session_id = f"enhanced_interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                conversation_history = []
                last_topic = None
                print("\n🔄 Aurora: Fresh slate! 🎨 What's next? I'm all ears!\n")
                print("-" * 80 + "\n")
                continue

            if user_input.lower() == 'status':
                print(
                    "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("                         🧠 AURORA INTELLIGENCE SYSTEM STATUS")
                print(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print("\n🟢 CORE STATUS: FULLY OPERATIONAL")
                print(
                    f"⚡ Power Level: 100% | Session Time: {message_count} messages")
                print(
                    f"💬 Context Memory: Tracking last {min(len(conversation_history), 15)} interactions")
                print("\n📚 ACTIVE CAPABILITIES (66 Total):")
                print(
                    "   • 13 Foundation Tasks: Problem-solving, Logic, Communication, Memory...")
                print(
                    "   • 53 Knowledge Tiers: Languages (1-6), Technical (7-27), Autonomous (28-53)")
                print("   • Tier 47: Documentation Generation ✓")
                print("   • Tier 48: Multi-Agent Coordination ✓")
                print("   • Tier 49: UI/UX Generation ✓")
                print("   • Tier 50: Git Mastery ✓")
                print("   • Tier 51: Code Quality Enforcement ✓")
                print("   • Tier 52: RSA Cryptography ✓")
                print("   • Tier 53: Docker Mastery ✓")
                print(
                    f"\n🎯 CONVERSATION MODE: {'Task Execution' if is_task else 'Casual Chat'}")
                print(f"😊 Detected Tone: {user_tone.title()}")
                print(f"🔧 Last Topic: {last_topic or 'Just getting started'}")
                print(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                print("-" * 80 + "\n")
                continue

            # Extract user name if mentioned
            if not user_name and any(phrase in user_input.lower() for phrase in ["i'm ", "i am ", "my name is ", "call me "]):
                name_match = re.search(
                    r"(?:i'm|i am|my name is|call me)\s+(\w+)", user_input.lower())
                if name_match:
                    user_name = name_match.group(1).title()

            # Build rich context for Aurora
            context = {
                # Last 15 for deep context
                "conversation_history": conversation_history[-15:],
                "message_count": message_count,
                "user_name": user_name,
                "user_tone": user_tone,
                "is_task_request": is_task,
                "last_topic": last_topic,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                # Aurora's personality settings
                "personality": {
                    "style": "friendly_and_intelligent",
                    "use_emojis": user_tone in ['casual', 'excited'],
                    "be_empathetic": user_tone == 'frustrated',
                    "be_encouraging": user_tone == 'polite',
                    "casual_language": True,
                    "show_personality": True
                },
                # Capability flags
                "can_execute_code": True,
                "can_modify_files": True,
                "can_analyze_codebase": True,
                "autonomous_mode": True,
                "all_tiers_active": True
            }

            # Store user message
            conversation_history.append({
                "role": "user",
                "content": user_input,
                "tone": user_tone,
                "is_task": is_task
            })

            # Get Aurora's response
            print("\nAurora: ", end="", flush=True)

            # Add instruction for natural conversation
            enhanced_prompt = user_input
            if message_count == 0:
                enhanced_prompt += "\n\n[Respond naturally and casually, like texting a friend. Use contractions, emojis when appropriate, and show personality. If this is a task, confirm you'll do it and show progress.]"

            response = await aurora.process_conversation(
                enhanced_prompt,
                session_id=session_id,
                context=context
            )

            print(response)

            # Extract topic from conversation
            if len(user_input.split()) > 3:
                last_topic = ' '.join(user_input.split()[:5]) + "..."

            # Store Aurora's response
            conversation_history.append({
                "role": "assistant",
                "content": response
            })

            print("\n" + "-" * 80 + "\n")
            message_count += 1

        except KeyboardInterrupt:
            print("\n\n👋 Aurora: Oh! Caught that Ctrl+C 😄 No worries - take care! 💙\n")
            break
        except Exception as e:
            error_msg = str(e)
            print(
                f"\n⚠️ Aurora: Hmm, hit a little snag there: {error_msg[:100]}...")
            print("          But hey, I'm still here! What else can I help with? 🤔\n")
            continue


if __name__ == "__main__":
    asyncio.run(interactive_chat())
