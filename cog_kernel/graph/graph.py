#!/usr/bin/env python3
"""
Simple reasoning graph:
- nodes represent modules/agents/memories
- edges represent dependencies or data flows with weights
- provides basic topological traversal and influence scoring
"""
import networkx as nx
from typing import Any

class ReasoningGraph:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_node(self, nid, meta=None):
        self.G.add_node(nid, meta=meta or {})

    def add_edge(self, a, b, weight=1.0):
        self.G.add_edge(a, b, weight=weight)

    def importance(self, node):
        # simplistic: PageRank score
        pr = nx.pagerank(self.G)
        return pr.get(node, 0.0)

    def topo(self):
        return list(nx.topological_sort(self.G))
