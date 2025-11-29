"""
Aurora Complete System Analysis
Let Aurora analyze ALL her systems and identify ALL issues
"""
import json
from aurora_core import AuroraCoreIntelligence
import sys
sys.path.insert(0, '.')


print("\n" + "="*80)
print("🔍 AURORA COMPLETE SYSTEM ANALYSIS")
print("="*80 + "\n")

aurora = AuroraCoreIntelligence()

# Ask Aurora to analyze herself completely
analysis_request = """
Aurora, I need you to do a COMPLETE analysis of your entire system.
Not just the chat, but EVERYTHING.

Analyze and report on:

1. **Chat System Issues:**
   - Re-greeting problems
   - Response quality issues
   - Memory/session persistence problems
   - Debug output leaking into responses
   - Any other chat-related bugs

2. **Backend Architecture:**
   - Python/TypeScript integration problems
   - API endpoint issues
   - Server stability problems
   - Performance bottlenecks

3. **Frontend/UI:**
   - Next.js compilation errors
   - React component issues
   - Styling/display problems
   - Navigation/routing issues

4. **Core Intelligence:**
   - NLP analysis accuracy
   - Code generation quality
   - Autonomous systems functionality
   - Learning/adaptation capabilities

5. **File System Organization:**
   - Duplicate files or confusion
   - Missing critical files
   - Architectural inconsistencies
   - Version conflicts

6. **Integration Points:**
   - Python ↔ TypeScript bridge reliability
   - Session management
   - Error handling gaps
   - Monitoring/logging issues

7. **Infrastructure:**
   - Port configuration problems
   - Process management issues
   - Build/compilation errors
   - Dependency conflicts

For EACH issue found, provide:
- **Issue**: Clear description
- **Severity**: Critical/High/Medium/Low
- **Impact**: What breaks or degrades
- **Root Cause**: Technical reason
- **Fix**: Specific solution

Be BRUTALLY HONEST. Don't sugarcoat anything. I need to know EVERY problem.
"""

# Get Aurora's analysis
analysis = aurora.analyze_natural_language(analysis_request)
context = aurora.get_conversation_context('system-analysis')
response = aurora.generate_aurora_response(
    analysis, context, 'system-analysis')

print(response)
print("\n" + "="*80)

# Save to file
output = {
    "timestamp": context["created_at"],
    "analysis": response,
    "severity_counts": {
        "critical": response.lower().count("critical"),
        "high": response.lower().count("high"),
        "medium": response.lower().count("medium"),
        "low": response.lower().count("low")
    }
}

with open("AURORA_COMPLETE_SYSTEM_ANALYSIS.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n✅ Analysis saved to AURORA_COMPLETE_SYSTEM_ANALYSIS.json")
print("="*80 + "\n")
