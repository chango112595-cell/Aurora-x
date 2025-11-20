#!/usr/bin/env python3
"""Ask Aurora to fix Python extension loading issues"""
import asyncio
from aurora_core import create_aurora_core


async def main():
    print("🔧 Asking Aurora to fix Python extension loading issues...\n")

    aurora = create_aurora_core()

    task = """The Python extension in VS Code is having loading issues. 

Please diagnose and fix:
1. Large files causing performance issues (tools/luminar_nexus.py is 4000+ lines)
2. Linter configuration overwhelming the extension
3. VS Code settings that need optimization for Python
4. File watcher and analysis settings

Check .vscode/settings.json and suggest optimizations."""

    response = await aurora.process_conversation(task, "fix_python_extension")

    print("="*80)
    print("AURORA'S RESPONSE:")
    print("="*80)
    print(response)
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
