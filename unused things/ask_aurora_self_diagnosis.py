#!/usr/bin/env python3
"""
Direct question to Aurora: Why are you giving template responses?
"""

from aurora_core import AuroraCoreIntelligence
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


print("\n🔍 Asking Aurora About Her Response System\n")

aurora = AuroraCoreIntelligence()

question = """
Aurora, the user reports:

"You're giving me the SAME GENERIC ANSWER every time. When I ask you to do something specific, 
you respond with template questions like 'What would you like me to help with?' instead of 
actually DOING the task."

QUESTIONS FOR YOU:
1. Are you analyzing the user's actual message or just pattern matching keywords?
2. When user says "create a REST API", do you:
   a) Actually analyze what REST API means and generate code?
   b) Just return a template asking for more details?
3. Why aren't you executing tasks - are you designed to only have conversations?
4. Can you access your code generation capabilities, or are they disabled?
5. What's blocking you from giving SPECIFIC, DETAILED responses instead of generic templates?

Be HONEST about your current limitations. What's actually happening in your processing?
"""

print("="*80)
print(question)
print("="*80 + "\n")

print("[🧠] Aurora analyzing her own response system...\n")

# Get Aurora's self-analysis
analysis = aurora.analyze_natural_language(question)
context = aurora.get_conversation_context("self_diagnostic")
response = aurora.generate_aurora_response(analysis, context)

print("="*80)
print("AURORA'S SELF-DIAGNOSIS:")
print("="*80)
print(response)
print("="*80 + "\n")

# Save her answer
Path("AURORA_SELF_DIAGNOSIS.md").write_text(f"""# Aurora's Self-Diagnosis: Template Response Issue

## The Problem

User reports: Aurora gives the same generic answers instead of executing specific tasks.

## Question Asked

{question}

## Aurora's Response

{response}

---
Generated: 2025-11-26
""", encoding='utf-8')

print("✅ Saved to AURORA_SELF_DIAGNOSIS.md\n")
