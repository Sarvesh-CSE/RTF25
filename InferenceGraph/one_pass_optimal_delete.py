#!/usr/bin/env python3
"""

Combines build_hypergraph.py + optimal_delete.py with all optimizations:
- Cost computation during construction
- Direct node references (no find_node)
"""

import sys
import os
from typing import Any, Dict, Set, List, Tuple
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cell import Attribute, Cell, Hyperedge
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row


class Node:
    """
    Represents a database cell in the RTF dependency graph.
    
    Each node tracks:
    - cell: The database cell this node represents
    - branches: List of (hyperedge, children) representing dependencies  
    - cost: Total cost to delete this cell and handle all its constraints
    """
    def __init__(self, cell: Cell):
        self.cell = cell
        self.branches = []
        self.cost = 1

    def add_branch(self, he: Hyperedge, children: List['Node']):
        """Add a hyperedge branch and update deletion costs."""
        self.branches.append((he, children))
        
        if children:
            # Find the cheapest child to delete for this specific hyperedge
            # (We only need to delete ONE child to break the constraint)
            min_child = children[0]
            for child in children[1:]:
                if child.cost < min_child.cost:
                    min_child = child
            # Store the cheapest child for optimal deletion path
            he.min_node = min_child
            
            # Recalculate total cost for this node
            # Cost = 1 (delete self) + sum of cheapest deletions for ALL constraints
            total_cost = 1  # Base cost of deleting this node
            for hyperedge, hyperedge_children in self.branches:
                if hyperedge_children:
                    # Find cheapest child for each constraint this node is involved in
                    min_hyperedge_child = hyperedge_children[0]
                    for child in hyperedge_children[1:]:
                        if child.cost < min_hyperedge_child.cost:
                            min_hyperedge_child = child
                    total_cost += min_hyperedge_child.cost
            
            self.cost = total_cost


def build_tree(row: Dict, key: Any, start_attr: str, hyperedge_map: Dict) -> Tuple[Node, Dict[Cell, Node]]:
    """
    Build dependency tree starting from target attribute.
    Returns root node and mapping from cells to nodes.
    """
    attribute_to_node = {}  # Maps attribute names to their nodes
    cell_to_node_map = {}   # Maps cell objects to their nodes
    
    def build_node_recursively(current_attr: str, visited_attrs: Set[str]) -> Node:
        """Recursively build nodes for each attribute and its dependencies."""
        # Create cell object for current attribute
        current_cell = Cell(Attribute('adult_data', current_attr), key, row[current_attr])
        
        # Return existing node if already created (avoid duplicates)
        if current_attr in attribute_to_node:
            return attribute_to_node[current_attr]
        
        # Create new node and store in both mappings
        current_node = Node(current_cell)
        attribute_to_node[current_attr] = current_node
        cell_to_node_map[current_cell] = current_node
        
        # Process all hyperedges (constraints) involving this cell
        for hyperedge in hyperedge_map.get(current_cell, []):
            # Extract all attribute names from this hyperedge
            attributes_in_hyperedge = []
            for cell_in_dc in hyperedge:  # ALL cells in this denial constraint
                attributes_in_hyperedge.append(cell_in_dc.attribute.col)
            
            # Skip if all attributes already visited (prevents infinite cycles)
            all_attrs_already_visited = True
            for attr_name in attributes_in_hyperedge:
                if attr_name not in visited_attrs:
                    all_attrs_already_visited = False
                    break
            if all_attrs_already_visited:
                continue
            
            # Build child nodes for unvisited attributes
            child_nodes = []
            new_visited_set = visited_attrs.copy()
            for cell_in_dc in hyperedge:  # ALL cells in this denial constraint
                new_visited_set.add(cell_in_dc.attribute.col)
            
            for cell_in_dc in hyperedge:  # ALL cells in this denial constraint
                if cell_in_dc.attribute.col not in visited_attrs:  # Filter out head
                    child_node = build_node_recursively(cell_in_dc.attribute.col, new_visited_set)
                    child_nodes.append(child_node)
            
            # Add this hyperedge as a branch if we have children
            if child_nodes:
                current_node.add_branch(hyperedge, child_nodes)
        
        return current_node
    
    # Start building from the target attribute
    root_node = build_node_recursively(start_attr, {start_attr})
    return root_node, cell_to_node_map


def optimal_delete(target: Cell, cell_map: Dict[Cell, Node]) -> Set[Cell]:
    if target not in cell_map:
        return set()
    
    to_delete = {target}
    queue = deque([cell_map[target]])
    
    while queue:
        curr = queue.popleft()
        for he, _ in curr.branches:
            if hasattr(he, 'min_node') and he.min_node and he.min_node.cell not in to_delete:
                to_delete.add(he.min_node.cell)
                queue.append(he.min_node)
    
    return to_delete


def compute_deletion_set(key: Any, target_attr: str) -> Set[Cell]:
    """Main function: Optimized RTF deletion computation."""
    row = fetch_row(key)
    hyperedge_map = build_hyperedge_map(row, key, target_attr)
    root, cell_map = build_tree(row, key, target_attr, hyperedge_map)
    target_cell = Cell(Attribute('adult_data', target_attr), key, row[target_attr])
    return optimal_delete(target_cell, cell_map)


if __name__ == "__main__":
    deletion_set = compute_deletion_set(2, 'education')
    print(f"Cells to delete ({len(deletion_set)}):")
    for cell in sorted(deletion_set, key=lambda c: c.attribute.col):
        print(f"  {cell}")