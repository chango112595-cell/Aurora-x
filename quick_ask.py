#!/usr/bin/env python3
import asyncio
from aurora_core import create_aurora_core


async def main():
    aurora = create_aurora_core()
    response = await aurora.process_conversation(
        "VS Code is slow. luminar_nexus.py is 4000 lines. Should I split it into smaller files or exclude it from linting?",
        session_id="quick_vscode"
    )
    print(response)

asyncio.run(main())
