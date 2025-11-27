#!/usr/bin/env python3
"""
Ask Aurora: VS Code Performance Analysis
Let Aurora analyze the VS Code performance issues and provide her recommendations
"""

import asyncio

from aurora_core import create_aurora_core


async def ask_aurora():
    print("\n" + "=" * 80)
    print("🌟 ASKING AURORA: VS Code Performance Analysis")
    print("=" * 80 + "\n")

    aurora = create_aurora_core()

    question = """
    Aurora, I need your expert analysis on VS Code performance issues:
    
    CURRENT SITUATION:
    - VS Code is loading slowly
    - Python extension is struggling
    - Main culprit: tools/luminar_nexus.py (4,002 lines with 30+ linter warnings)
    - Workspace has 4,033+ files being indexed
    
    ISSUES FOUND IN luminar_nexus.py:
    - Multiple "Using open without explicitly specifying an encoding" warnings
    - Bare except clauses (except: pass)
    - Unreachable code sections
    - Unused arguments in functions
    - Attributes defined outside __init__
    - General Exception raises
    
    PROPOSED SOLUTION:
    Add VS Code settings to exclude luminar_nexus.py from analysis:
    ```json
    {
      "python.analysis.exclude": [
        "**/tools/luminar_nexus.py",
        "**/.venv/**",
        "**/node_modules/**"
      ],
      "files.watcherExclude": {
        "**/.venv/**": true,
        "**/node_modules/**": true,
        "**/__pycache__/**": true
      }
    }
    ```
    
    QUESTIONS:
    1. Do you think excluding luminar_nexus.py is a good idea, or should we fix it properly?
    2. Would splitting luminar_nexus.py into smaller modules be better long-term?
    3. Are there other optimizations you'd recommend for VS Code performance?
    4. Should we fix all the encoding warnings and bare excepts in luminar_nexus.py?
    5. What's your professional recommendation as an AI architect?
    
    Give me your honest analysis with pros/cons and your recommended action plan.
    """

    response = await aurora.process_conversation(question, session_id="vscode_performance_analysis")

    print("🧠 Aurora's Analysis:\n")
    print(response)
    print("\n" + "=" * 80)
    print("✅ Analysis Complete")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(ask_aurora())
