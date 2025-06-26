#!/usr/bin/env python3
"""
Compact RTF (Right To Be Forgotten) Analysis
Tests single vs batch deletion performance
"""

import sys
import os
import argparse
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import InferenceGraph components
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row
from InferenceGraph.build_hypergraph import build_hypergraph_tree
from InferenceGraph.optimal_delete import optimal_delete
from InferenceGraph.one_pass_optimal_delete import compute_deletion_set
from cell import Cell, Attribute
import db_wrapper

def get_row_keys(num_rows):
    """Get row keys from database"""
    db = db_wrapper.DatabaseWrapper(db_wrapper.DatabaseConfig())
    rows = db.execute_query(f"SELECT id FROM adult_data LIMIT {num_rows}")
    keys = [row['id'] for row in rows]
    db.close()
    return keys

def single_analysis(key, target_attr):
    """Single row deletion analysis"""
    print(f"=== Single Row Analysis ===")
    print(f"Key: {key}, Target: {target_attr}")
    
    # Build components
    row = fetch_row(key)
    hyperedge_map = build_hyperedge_map(row, key, target_attr)
    target_cell = Cell(Attribute('adult_data', target_attr), key, row[target_attr])
    root = build_hypergraph_tree(row, key, target_attr, hyperedge_map)
    
    # Time both algorithms
    start = time.time()
    one_pass_set = compute_deletion_set(key, target_attr)
    one_pass_time = time.time() - start
    
    start = time.time()
    traditional_set = optimal_delete(root, target_cell)
    traditional_time = time.time() - start
    
    # Results
    speedup = traditional_time / one_pass_time if one_pass_time > 0 else 0
    print(f"Graph: {len(hyperedge_map)} cells")
    print(f"One-pass: {len(one_pass_set)} cells in {one_pass_time:.4f}s")
    print(f"Traditional: {len(traditional_set)} cells in {traditional_time:.4f}s")
    print(f"Speedup: {speedup:.2f}x {'(One-pass wins)' if speedup > 1 else '(Traditional wins)'}")
    
    return len(one_pass_set)

def batch_analysis(target_attr, num_rows):
    """Batch deletion analysis"""
    print(f"=== Batch Analysis ===")
    print(f"Target: {target_attr}, Rows: {num_rows}")
    
    keys = get_row_keys(num_rows)
    print(f"Processing {len(keys)} rows...")
    
    # One-pass batch
    start = time.time()
    one_pass_total = 0
    for key in keys:
        try:
            deletion_set = compute_deletion_set(key, target_attr)
            one_pass_total += len(deletion_set)
        except:
            pass
    one_pass_time = time.time() - start
    
    # Traditional batch
    start = time.time()
    traditional_total = 0
    for key in keys:
        try:
            row = fetch_row(key)
            hyperedge_map = build_hyperedge_map(row, key, target_attr)
            root = build_hypergraph_tree(row, key, target_attr, hyperedge_map)
            target_cell = Cell(Attribute('adult_data', target_attr), key, row[target_attr])
            deletion_set = optimal_delete(root, target_cell)
            traditional_total += len(deletion_set)
        except:
            pass
    traditional_time = time.time() - start
    
    # Results
    speedup = traditional_time / one_pass_time if one_pass_time > 0 else 0
    ops_per_sec_one = one_pass_total / one_pass_time if one_pass_time > 0 else 0
    ops_per_sec_trad = traditional_total / traditional_time if traditional_time > 0 else 0
    
    print(f"One-pass: {one_pass_total} cells in {one_pass_time:.3f}s ({ops_per_sec_one:.0f} ops/sec)")
    print(f"Traditional: {traditional_total} cells in {traditional_time:.3f}s ({ops_per_sec_trad:.0f} ops/sec)")
    print(f"Speedup: {speedup:.2f}x {'🚀 One-pass wins!' if speedup > 1 else '🐌 Traditional wins'}")
    
    return one_pass_total

def main():
    parser = argparse.ArgumentParser(description='Compact RTF Analysis')
    parser.add_argument('--key', '-k', type=int, default=2, help='Row key (single mode)')
    parser.add_argument('--attr', '-a', default='education', help='Target attribute')
    parser.add_argument('--batch', '-b', type=int, help='Batch mode: number of rows')
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            cells_deleted = batch_analysis(args.attr, args.batch)
        else:
            cells_deleted = single_analysis(args.key, args.attr)
        
        print(f"\n✅ Analysis complete: {cells_deleted} total cells deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()