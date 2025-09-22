from typing import Any, List, Tuple, Dict, Set

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path for import resolution
from cell import Attribute, Cell, Hyperedge
from InferenceGraph.bulid_hyperedges import HyperedgeBuilder
from fetch_row import RTFDatabaseManager



# ----------------------------------------------------------------------------- 
class GraphNode:
    """
    A node in the hyperedge inference tree.  Each branch is a (hyperedge, child_nodes) pair.
    """
    def __init__(self, cell: Cell):
        self.cell: Cell = cell # Cell is your (table, column, value, key) object.
        self.branches: List[Tuple[Hyperedge, List['GraphNode']]] = []

    def add_branch(self, he: Hyperedge, children: List['GraphNode']) -> None:
        self.branches.append((he, children))

    def pretty_print(self, indent: int = 0) -> None:
        # Print this node
        print("  " * indent + repr(self.cell))
        # Then each hyperedge and its subtree
        for he, children in self.branches:
            print("  " * (indent + 1) + repr(he))
            for child in children:
                child.pretty_print(indent + 2)

def build_hypergraph_tree(
    row: Dict[str, Any],
    key: Any,
    start_attr: str,
    hyperedge_map: Dict[Cell, List[Hyperedge]] # hem (hyperedge‐map) tells you, for any head Cell, which hyperedges to expand.
) -> GraphNode:
    """
    Build an in-memory tree of GraphNode from start_attr, using BFS-derived hyperedge_map.
    Returns the root GraphNode.
    """
    visited: Set[str] = {start_attr}
    node_map: Dict[str, GraphNode] = {}

    def recurse(attr: str, snapshot: Set[str]) -> GraphNode:
        # 1) Create or reuse the node for this attribute
        cell = Cell(Attribute('adult_data', attr), key, row[attr])
        if attr in node_map:
            return node_map[attr]
        node = GraphNode(cell)
        node_map[attr] = node
        current_snapshot = set(snapshot)
         # 2) For each hyperedge where this cell is the head...
        for he in hyperedge_map.get(cell, []):
            tail_cells = list(he)
            tail_attrs = [tc.attribute.col for tc in tail_cells]
            # 3) Skip if all tail attributes already in this path
            if all(t in current_snapshot for t in tail_attrs):
                continue
            
            # 4) Otherwise, recurse on each unseen tail
            new_snapshot = current_snapshot.union(tail_attrs)
            child_nodes: List[GraphNode] = []
            
            for tc in tail_cells:
                if tc.attribute.col not in current_snapshot:
                    child = recurse(tc.attribute.col, new_snapshot)
                    child_nodes.append(child)
            # 5) Attach the branch (he, children) to our node
            node.add_branch(he, child_nodes)

        return node
     # Kick off recursion from the start attribute
    return recurse(start_attr, visited)

def main():
    key = 2
    with RTFDatabaseManager('adult') as db:
        row = db.fetch_row(key)
    root_attr = 'education'
    builder = HyperedgeBuilder(dataset='adult')
    hyperedge_map = builder.build_hyperedge_map(row, key, root_attr)
    root = build_hypergraph_tree(row, key, root_attr, hyperedge_map)
    root.pretty_print()

if __name__ == '__main__':
    main()