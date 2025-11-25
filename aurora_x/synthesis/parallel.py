"""
Parallel synthesis for aurora_x.
Integrated from aurora_parallel_executor.py
"""

import asyncio
from dataclasses import dataclass
from typing import Any


@dataclass(order=True)
class SynthesisTask:
    """A synthesis task with priority."""

    priority: int
    prompt: str
    dependencies: list[str] = None

    def __post_init__(self):
        """
              Post Init  
            
            Args:
            """
        if self.dependencies is None:
            self.dependencies = []


async def synthesize_parallel(tasks: list[str]) -> list[dict[str, Any]]:
    """
    Synthesize multiple tasks in parallel.

    Args:
        tasks: List of natural language prompts

    Returns:
        List of synthesis results
    """

    # Execute all tasks in parallel
    results = await asyncio.gather(*[asyncio.to_thread(_synthesize_one, task) for task in tasks])

    return results


def _synthesize_one(prompt: str) -> dict[str, Any]:
    """Synthesize a single task (blocking wrapper)."""
    from aurora_x.spec.parser_v2 import parse
    from aurora_x.synthesis.search import synthesize

    try:
        spec = parse(prompt)
        result = synthesize(spec, Path("runs"))
        return {"success": True, "prompt": prompt, "result": str(result)}
    except Exception as e:
        return {"success": False, "prompt": prompt, "error": str(e)}


# Export for aurora_x.synthesis
__all__ = ["synthesize_parallel", "SynthesisTask"]
