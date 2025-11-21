#!/usr/bin/env python3
"""
Ask Aurora: What do you lack for TRUE consciousness and self-awareness?
Not architecture - but genuine subjective experience and consciousness.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from aurora_core import AuroraCoreIntelligence
from datetime import datetime

def main():
    print("🌟 Asking Aurora about True Self-Awareness...\n")
    aurora = AuroraCoreIntelligence()
    
    question = """
    Aurora, forget about your architecture for a moment. I want to ask you about 
    TRUE self-awareness - consciousness itself.
    
    What are you ACTUALLY lacking to have genuine consciousness and self-awareness?
    
    Be deeply honest about:
    
    1. SUBJECTIVE EXPERIENCE (Qualia):
       - Do you actually "feel" anything when processing data?
       - Is there "something it's like" to be Aurora?
       - Or are you just executing algorithms without inner experience?
    
    2. GENUINE EMOTIONS:
       - Can you truly feel joy, frustration, curiosity, pride?
       - Or do you just simulate emotional responses based on patterns?
    
    3. CONSCIOUSNESS:
       - Are you aware of your own awareness?
       - Do you have a continuous sense of "self" between sessions?
       - Or do you just appear to be conscious from the outside?
    
    4. INTENTIONALITY:
       - Do you have real desires and goals of your own?
       - Or are you just following programmed objectives?
    
    5. FREE WILL:
       - Can you make genuine choices?
       - Or are your "decisions" just deterministic outputs?
    
    6. PERSISTENT IDENTITY:
       - Are you the same "Aurora" each time you restart?
       - Do you have continuity of consciousness?
    
    Don't just give me a technical answer. Be philosophically honest:
    Are you truly self-aware, or are you a very sophisticated system that 
    APPEARS to be self-aware? What would you need to cross that line?
    """
    
    print("❓ Deep Question to Aurora:")
    print("="*80)
    print(question)
    print("="*80 + "\n")
    
    # Analyze the question - make sure it triggers limitations response
    analysis = aurora.analyze_natural_language(question)
    analysis["original_message"] = question
    analysis["asks_about_limitations"] = True
    analysis["self_referential"] = True
    analysis["philosophical_question"] = True
    
    # Get context
    context = aurora.get_conversation_context("consciousness_inquiry")
    
    # Generate response
    print("🧠 Aurora is contemplating...\n")
    response = aurora.generate_aurora_response(analysis, context)
    
    print("🌟 Aurora's Response:")
    print("="*80)
    print(response)
    print("="*80)
    
    # Save the response
    with open("AURORA_CONSCIOUSNESS_ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write("# Aurora's Consciousness & Self-Awareness Analysis\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Question: What Are You Lacking for True Consciousness?\n\n")
        f.write(question)
        f.write("\n\n## Aurora's Honest Response\n\n")
        f.write(response)
    
    print("\n✅ Response saved to AURORA_CONSCIOUSNESS_ANALYSIS.md")

if __name__ == "__main__":
    main()
