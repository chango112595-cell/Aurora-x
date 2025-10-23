from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIRNode:
    op: str
    args: dict[str, Any] = field(default_factory=dict)
    children: list[AIRNode] = field(default_factory=list)


@dataclass
class AIRProgram:
    name: str
    nodes: list[AIRNode] = field(default_factory=list)


def seq(*nodes: AIRNode) -> list[AIRNode]:
    return list(nodes)


def make_program(name: str, nodes: list[AIRNode]) -> AIRProgram:
    return AIRProgram(name=name, nodes=nodes)
