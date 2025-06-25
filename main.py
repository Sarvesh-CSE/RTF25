#!/usr/bin/env python3
"""
Compact RTF script focusing on InferenceGraph components only
"""

import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import InferenceGraph components
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row
from InferenceGraph.build_hypergraph import build_hypergraph_tree
from InferenceGraph.optimal_delete import optimal_delete
from InferenceGraph.one_pass_optimal_delete import compute_deletion_set
from cell import Cell, Attribute

def run_inference_analysis(key: int, target_attr: str):
    """Run complete inference graph analysis"""
    print(f"=== RTF Inference Analysis ===")
    print(f"Key: {key}, Target: {target_attr}")
    
    try:
        # 1. Fetch data and build hyperedges
        row = fetch_row(key)
        hyperedge_map = build_hyperedge_map(row, key, target_attr)
        target_cell = Cell(Attribute('adult_data', target_attr), key, row[target_attr])
        
        print(f"\n1. Target cell: {target_cell}")
        print(f"2. Built hyperedge map for {len(hyperedge_map)} cells")
        
        # 2. Build hypergraph tree
        root = build_hypergraph_tree(row, key, target_attr, hyperedge_map)
        print(f"3. Built hypergraph tree with {len(root.branches)} branches")
        
        # 3. Compute optimal deletion (one-pass) - timed
        import time
        start_time = time.time()
        deletion_set = compute_deletion_set(key, target_attr)
        one_pass_time = time.time() - start_time
        
        print(f"\n4. One-pass algorithm: {len(deletion_set)} cells in {one_pass_time:.4f}s")
        for cell in sorted(deletion_set, key=lambda c: c.attribute.col):
            print(f"   {cell}")
        
        # 4. Compare with traditional algorithm - timed
        try:
            start_time = time.time()
            traditional_set = optimal_delete(root, target_cell)
            traditional_time = time.time() - start_time
            
            print(f"\n5. Traditional algorithm: {len(traditional_set)} cells in {traditional_time:.4f}s")
            
            # Compare results
            if len(traditional_set) == len(deletion_set):
                speedup = traditional_time / one_pass_time if one_pass_time > 0 else float('inf')
                print("Same deletion set size")
                print(f" Speedup: {speedup:.2f}x faster")
            else:
                print(f" Different deletion set sizes - check algorithms!")
                
        except Exception as e:
            print(f"5. Traditional algorithm failed: {e}")
        
        return len(deletion_set)
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description='Compact RTF Inference Analysis')
    parser.add_argument('--key', '-k', type=int, default=2, help='Row key')
    parser.add_argument('--attr', '-a', default='education', help='Target attribute')
    
    args = parser.parse_args()
    
    deletion_count = run_inference_analysis(args.key, args.attr)
    print(f"\n=== Analysis Complete ===")
    print(f"Cells to delete: {deletion_count}")

if __name__ == "__main__":
    main()