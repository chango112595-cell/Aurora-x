from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class AIRNode:
    op: str
    args: Dict[str, Any] = field(default_factory=dict)
    children: List["AIRNode"] = field(default_factory=list)

@dataclass
class AIRProgram:
    name: str
    nodes: List[AIRNode] = field(default_factory=list)

def seq(*nodes: AIRNode) -> List[AIRNode]:
    return list(nodes)

def make_program(name: str, nodes: List[AIRNode]) -> AIRProgram:
    return AIRProgram(name=name, nodes=nodes)
