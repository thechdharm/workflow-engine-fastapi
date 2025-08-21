from typing import Optional, List, Dict, Any

def first_node(graph: Dict[str, Any]) -> Optional[str]:
    # try edge out of an explicit 'start' node first
    start_id = "start"
    if any(n.get("id") == start_id for n in graph.get("nodes", [])):
        for e in graph.get("edges", []):
            if e.get("source") == start_id:
                return e.get("target")
    # else: find any node with no incoming edges (excluding 'start')
    nodes = {n["id"] for n in graph.get("nodes", []) if n["id"] != "start"}
    incoming = {e["target"] for e in graph.get("edges", [])}
    roots = list(nodes - incoming)
    return roots[0] if roots else None

def next_nodes(node_id: str, graph: Dict[str, Any]) -> List[str]:
    return [e["target"] for e in graph.get("edges", []) if e.get("source") == node_id]

def find_node(node_id: str, graph: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for n in graph.get("nodes", []):
        if n.get("id") == node_id:
            return n
    return None
