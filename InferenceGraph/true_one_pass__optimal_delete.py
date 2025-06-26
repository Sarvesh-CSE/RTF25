#!/usr/bin/env python3
"""
Optimized one-pass optimal deletion algorithm
Eliminates redundant cost computations during tree construction
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
    Optimized node that defers cost computation until tree is fully built.
    This eliminates the O(n²) overhead of recomputing costs on every branch addition.
    """
    def __init__(self, cell: Cell):
        self.cell = cell
        self.branches = []
        self.cost = None  # Computed lazily
        self.is_finalized = False

    def add_branch(self, he: Hyperedge, children: List['Node']):
        """Add branch without computing costs - deferred until finalization"""
        self.branches.append((he, children))

    def finalize_cost(self):
        """
        Compute cost in single post-order traversal after tree construction.
        This is the key optimization - costs computed once, not on every addition.
        """
        if self.is_finalized:
            return self.cost
        
        if not self.branches:
            # Leaf node - base cost
            self.cost = 1
        else:
            # Internal node - compute from finalized children
            total_cost = 1  # Cost of deleting this node
            
            for he, children in self.branches:
                if children:
                    # Ensure all children are finalized first
                    for child in children:
                        child.finalize_cost()
                    
                    # Find minimum cost child for this hyperedge
                    min_child = min(children, key=lambda c: c.cost)
                    he.min_node = min_child  # Store for deletion path
                    total_cost += min_child.cost
            
            self.cost = total_cost
        
        self.is_finalized = True
        return self.cost


def build_optimized_tree(row: Dict, key: Any, start_attr: str, hyperedge_map: Dict) -> Tuple[Node, Dict[Cell, Node]]:
    """
    Build dependency tree with optimized cost computation.
    Returns root node and O(1) lookup map for cells.
    """
    attribute_to_node = {}  # Maps attribute names to nodes
    cell_to_node_map = {}   # Maps cell objects to nodes for O(1) lookup
    
    def build_node_recursively(current_attr: str, visited_attrs: Set[str]) -> Node:
        """Recursively build nodes with deferred cost computation"""
        # Create cell object for current attribute
        current_cell = Cell(Attribute('adult_data', current_attr), key, row[current_attr])
        
        # Return existing node if already created
        if current_attr in attribute_to_node:
            return attribute_to_node[current_attr]
        
        # Create new node
        current_node = Node(current_cell)
        attribute_to_node[current_attr] = current_node
        cell_to_node_map[current_cell] = current_node
        
        # Process all hyperedges involving this cell
        for hyperedge in hyperedge_map.get(current_cell, []):
            # Extract attributes from this hyperedge
            attributes_in_hyperedge = [cell.attribute.col for cell in hyperedge]
            
            # Skip if all attributes already visited (prevents cycles)
            if all(attr in visited_attrs for attr in attributes_in_hyperedge):
                continue
            
            # Build child nodes for unvisited attributes
            child_nodes = []
            new_visited_set = visited_attrs | set(attributes_in_hyperedge)
            
            # Sort for deterministic behavior
            for cell_in_dc in sorted(hyperedge, key=lambda c: c.attribute.col):
                if cell_in_dc.attribute.col not in visited_attrs:
                    child_node = build_node_recursively(cell_in_dc.attribute.col, new_visited_set)
                    child_nodes.append(child_node)
            
            # Add branch without cost computation
            if child_nodes:
                current_node.add_branch(hyperedge, child_nodes)
        
        return current_node
    
    # Build tree structure without computing costs
    root_node = build_node_recursively(start_attr, {start_attr})
    
    # Compute all costs in single post-order traversal
    root_node.finalize_cost()
    
    return root_node, cell_to_node_map


def optimal_delete_optimized(target: Cell, cell_map: Dict[Cell, Node]) -> Set[Cell]:
    """
    Optimized deletion using pre-computed costs and O(1) node lookup.
    Eliminates expensive find_node() calls from traditional algorithm.
    """
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
    """
    Main function: Optimized one-pass deletion computation.
    
    Key optimizations:
    1. Deferred cost computation (eliminates O(n²) overhead)
    2. O(1) cell-to-node mapping (eliminates find_node() calls)
    3. Single post-order traversal for cost finalization
    """
    # Build hyperedge map
    row = fetch_row(key)
    hyperedge_map = build_hyperedge_map(row, key, target_attr)
    
    # Build optimized tree with deferred costs
    root, cell_map = build_optimized_tree(row, key, target_attr, hyperedge_map)
    
    # Perform deletion with O(1) lookups
    target_cell = Cell(Attribute('adult_data', target_attr), key, row[target_attr])
    return optimal_delete_optimized(target_cell, cell_map)


if __name__ == "__main__":
    # Test the optimized algorithm
    deletion_set = compute_deletion_set(2, 'education')
    print(f"Optimized algorithm found {len(deletion_set)} cells to delete:")
    for cell in sorted(deletion_set, key=lambda c: c.attribute.col):
        print(f"  {cell}")