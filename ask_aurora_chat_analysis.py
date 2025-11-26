"""
Ask Aurora to analyze her own chat system - FORCE DEEP ANALYSIS
"""
from aurora_core import AuroraCoreIntelligence
import sys
sys.path.insert(0, '.')

aurora = AuroraCoreIntelligence()

# Create analysis question that triggers architectural analysis
question = """Aurora, diagnose your own chat system architecture and analyze these critical issues:

OBSERVED PROBLEMS:
1. Frontend creates new sessionId on every page refresh (Date.now()) - memory doesn't persist across refreshes
2. You re-greeted user on 4th message - context seems to reset randomly
3. You don't provide lists when asked for specific items
4. Backend spawns NEW Python process for each message (~800ms overhead)
5. Technical questions get generic "Looking at X - I can help" instead of actual analysis

TECHNICAL DETAILS:
- Frontend: AuroraFuturisticChat.tsx with useState sessionId
- Backend: aurora-chat.ts spawns Python with child_process
- Intelligence: aurora_core.py generate_aurora_response()
- Session storage: .aurora/sessions/{session_id}.json

YOUR TASK - ANALYZE AND PROVIDE:
1. Why does session persist to disk but frontend loses it on refresh?
2. Why do you re-greet after several messages?
3. How to make you provide structured responses (lists, bullet points)?
4. Should we use long-running Python process or keep spawning?
5. Specific code fixes for each issue

BE SPECIFIC. PROVIDE CODE. NO GENERIC RESPONSES."""

# Force architectural analysis path
analysis = aurora.analyze_natural_language(question)
analysis["intent"] = "technical_aurora_analysis"  # Force the right path

context = aurora.get_conversation_context('aurora-deep-analysis')
response = aurora.generate_aurora_response(
    analysis, context, 'aurora-deep-analysis')

print("=" * 80)
print("AURORA'S DEEP SYSTEM ANALYSIS:")
print("=" * 80)
print(response)
print("=" * 80)
print("\nSession saved to: .aurora/sessions/aurora-deep-analysis.json")
