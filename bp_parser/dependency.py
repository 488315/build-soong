# bp_parser/dependency.py

from typing import List, Dict
from bp_parser.ast import BpModule


def build_dependency_graph(modules: List[BpModule]) -> Dict[str, List[str]]:
    graph = {}
    for mod in modules:
        graph[mod.name] = mod.deps
    return graph


def detect_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
    visited = set()
    stack = []
    cycles = []

    def visit(node, path):
        if node in path:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        for dep in graph.get(node, []):
            visit(dep, path + [node])

    for n in graph:
        visit(n, [])

    return cycles
