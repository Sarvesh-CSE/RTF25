from typing import Any, List, Tuple, Dict, Set
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path for import resolution
import db_wrapper as dbw
from cell import Attribute, Cell, Hyperedge
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row

# ----------------------------------------------------------------------------- 
class GraphNode:
    """
    A node in the hyperedge inference tree.  Each branch is a (hyperedge, child_nodes) pair.
    """
    def __init__(self, cell: Cell):
        self.cell: Cell = cell
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
    hyperedge_map: Dict[Cell, List[Hyperedge]]
) -> GraphNode:
    """
    Build an in-memory tree of GraphNode from start_attr, using BFS-derived hyperedge_map.
    Returns the root GraphNode.
    """
    visited: Set[str] = {start_attr}
    node_map: Dict[str, GraphNode] = {}

    def recurse(attr: str, snapshot: Set[str]) -> GraphNode:
        cell = Cell(Attribute('adult_data', attr), key, row[attr])
        if attr in node_map:
            return node_map[attr]
        node = GraphNode(cell)
        node_map[attr] = node
        current_snapshot = set(snapshot)

        for he in hyperedge_map.get(cell, []):
            tail_cells = list(he)
            tail_attrs = [tc.attribute.col for tc in tail_cells]
            # skip branches whose tails have all been seen
            if all(t in current_snapshot for t in tail_attrs):
                continue
            new_snapshot = current_snapshot.union(tail_attrs)
            child_nodes: List[GraphNode] = []
            for tc in tail_cells:
                if tc.attribute.col not in current_snapshot:
                    child = recurse(tc.attribute.col, new_snapshot)
                    child_nodes.append(child)
            node.add_branch(he, child_nodes)

        return node

    return recurse(start_attr, visited)

def main():
    key = 2
    row = fetch_row(key)
    root_attr = 'education'
    root_cell = Cell(Attribute('adult_data', root_attr), key, row[root_attr])
    root = build_hypergraph_tree(row, key, root_attr, build_hyperedge_map(row, key, root_attr))

    # Traverse or integrate optimal-delete logic:
    # for he, children in root.branches: ...
    root.pretty_print()

if __name__ == '__main__':
    main()