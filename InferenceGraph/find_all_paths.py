#!/usr/bin/env python3
"""
Script to find and list all paths from a target cell to leaves
in the RTF inference graph.
"""

import sys
import os
from typing import List

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cell import Cell
from fetch_row import RTFDatabaseManager
from InferenceGraph.bulid_hyperedges import HyperedgeBuilder
from InferenceGraph.build_hypergraph import build_hypergraph_tree, GraphNode

def find_all_paths(root: GraphNode, path: List[Cell], all_paths: List[List[Cell]]):
    """
    Recursively finds all paths from the root to any leaf node.
    """
    # Add the current node's cell to the path
    current_path = path + [root.cell]
    
    # Base case: If this is a leaf node, save the path
    if not root.branches:
        all_paths.append(current_path)
        return
        
    # Recursive step: Traverse each branch
    for _, children in root.branches:
        for child in children:
            find_all_paths(child, current_path, all_paths)

def main():
    """
    Main function to build the graph and find all paths.
    """
    # Define your target cell
    key = 2
    root_attr = 'education'

    print("Fetching row data...")
    # Call the function from the imported module
    with RTFDatabaseManager('adult') as fr:
        row = fr.fetch_row(key)
    print(f"Row fetched for key {key}: {row['education']}")

    print("\nBuilding hyperedge map...")
    # Instantiate the HyperedgeBuilder class to call its method
    builder = HyperedgeBuilder(dataset='adult')
    hyperedge_map = builder.build_hyperedge_map(row, key, root_attr)

    print("Building hypergraph tree...")
    root_node = build_hypergraph_tree(row, key, root_attr, hyperedge_map)
    
    if not root_node:
        print("Could not build a graph for the target cell. No paths to find.")
        return

    all_paths = []
    find_all_paths(root_node, [], all_paths)
    
    print(f"\nFound a total of {len(all_paths)} paths from the target cell.")
    print("\n--- Listing All Paths ---")
    for i, path in enumerate(all_paths, 1):
        path_str = " -> ".join([f"{cell.attribute.col}[{cell.value}]" for cell in path])
        print(f"Path {i}: {path_str}")

if __name__ == '__main__':
    main()