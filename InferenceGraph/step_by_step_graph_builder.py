# InferenceGraph/compact_graph_builder.py
"""
Compact script: Just the first 4 steps of inference graph construction
1. Fetch target row
2. Create target cell (root)  
3. Build hyperedge map
4. Show hyperedges connected to target
"""

import sys
import os

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cell import Cell, Attribute
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row


def build_target_hyperedges(target_key: int, target_attr: str):
    """
    Compact function: Build hyperedges for target cell only
    """
    print(f"=== Target Cell Hyperedges ===")
    print(f"Target: {target_attr} in row {target_key}")
    
    # Step 1: Fetch target row
    print(f"\nStep 1: Fetching target row...")
    row = fetch_row(target_key)
    print(f"  ✓ Fetched row {target_key}")
    
    # Step 2: Create target cell (root)
    print(f"\nStep 2: Creating target cell...")
    target_cell = Cell(Attribute('adult_data', target_attr), target_key, row[target_attr])
    print(f"  ✓ Target cell: {target_cell}")
    
    # Step 3: Build hyperedge map
    print(f"\nStep 3: Building hyperedge map...")
    hyperedge_map = build_hyperedge_map(row, target_key, target_attr)
    print(f"  ✓ Built hyperedge map with {len(hyperedge_map)} head cells")
    
    # Step 4: Show hyperedges connected to target
    print(f"\nStep 4: Hyperedges connected to target...")
    target_hyperedges = hyperedge_map.get(target_cell, [])
    print(f"  ✓ Found {len(target_hyperedges)} hyperedges for target cell")
    
    if target_hyperedges:
        for i, hyperedge in enumerate(target_hyperedges):
            print(f"    Hyperedge {i+1}: {len(hyperedge)} cells")
            for cell in hyperedge:
                print(f"      - {cell.attribute.col} = {cell.value}")
    else:
        print(f"    No hyperedges found for target cell")
    
    return target_cell, target_hyperedges


def main():
    """Demo with specific target"""
    build_target_hyperedges(target_key=2, target_attr='education')



if __name__ == "__main__":
    main()
    
    print(f"\n" + "="*50)
