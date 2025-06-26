#!/usr/bin/env python3
"""
Compact RTF deletion performance evaluator.
Measures: Query Time | Graph Building | Deletion Computation | Total | Memory
"""

import sys
import os
import time
import tracemalloc
from typing import List, Tuple, Set
from dataclasses import dataclass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cell import Attribute, Cell
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row
from InferenceGraph.build_hypergraph import build_hypergraph_tree
from InferenceGraph.optimal_delete import optimal_delete, compute_costs, find_node
from InferenceGraph.one_pass_optimal_delete import compute_deletion_set as one_pass_deletion

@dataclass
class Metrics:
    query_time: float = 0.0
    graph_time: float = 0.0
    deletion_time: float = 0.0
    memory_mb: float = 0.0
    deletion_size: int = 0
    success: bool = True

def measure_approach(approach_name: str, eval_func, key: int, target_attr: str) -> Metrics:
    """Measure performance of a single approach."""
    try:
        tracemalloc.start()
        start = time.perf_counter()
        
        deletion_set = eval_func(key, target_attr)
        
        _, peak = tracemalloc.get_traced_memory()
        total_time = time.perf_counter() - start
        tracemalloc.stop()
        
        return Metrics(
            query_time=0.0,  # Set by individual evaluators
            graph_time=0.0,  # Set by individual evaluators  
            deletion_time=total_time,  # Default fallback
            memory_mb=peak / 1024 / 1024,
            deletion_size=len(deletion_set),
            success=True
        )
    except Exception as e:
        tracemalloc.stop()
        return Metrics(success=False)

def eval_multi_pass(key: int, target_attr: str) -> Set[Cell]:
    """Multi-pass approach with timing breakdown."""
    global last_metrics
    
    # Query time
    query_start = time.perf_counter()
    row = fetch_row(key)
    query_time = time.perf_counter() - query_start
    
    # Graph building
    graph_start = time.perf_counter()
    hyperedge_map = build_hyperedge_map(row, key, target_attr)
    root = build_hypergraph_tree(row, key, target_attr, hyperedge_map)
    graph_time = time.perf_counter() - graph_start
    
    # Deletion computation
    deletion_start = time.perf_counter()
    compute_costs(root)
    start_node = find_node(root, root.cell)
    deletion_set = optimal_delete(root, root.cell)
    deletion_time = time.perf_counter() - deletion_start
    
    # Store detailed timing
    last_metrics = Metrics(query_time=query_time, graph_time=graph_time, deletion_time=deletion_time)
    return deletion_set

def eval_one_pass(key: int, target_attr: str) -> Set[Cell]:
    """One-pass approach with timing breakdown."""
    global last_metrics
    
    # Query time
    query_start = time.perf_counter()
    row = fetch_row(key)
    query_time = time.perf_counter() - query_start
    
    # Combined computation
    combined_start = time.perf_counter()
    deletion_set = one_pass_deletion(key, target_attr)
    combined_time = time.perf_counter() - combined_start
    
    # Estimate breakdown (quick graph build for measurement)
    graph_start = time.perf_counter()
    build_hyperedge_map(row, key, target_attr)
    estimated_graph_time = time.perf_counter() - graph_start
    
    last_metrics = Metrics(
        query_time=query_time,
        graph_time=estimated_graph_time,
        deletion_time=combined_time - estimated_graph_time
    )
    return deletion_set

def eval_true_one_pass(key: int, target_attr: str) -> Set[Cell]:
    """True one-pass approach with timing breakdown."""
    global last_metrics
    from InferenceGraph.one_pass_optimal_delete import build_tree, optimal_delete as true_optimal
    
    # Query time
    query_start = time.perf_counter()
    row = fetch_row(key)
    query_time = time.perf_counter() - query_start
    
    # Graph building with integrated costs
    graph_start = time.perf_counter()
    hyperedge_map = build_hyperedge_map(row, key, target_attr)
    root, cell_map = build_tree(row, key, target_attr, hyperedge_map)
    graph_time = time.perf_counter() - graph_start
    
    # Deletion extraction
    deletion_start = time.perf_counter()
    target_cell = Cell(Attribute('adult_data', target_attr), key, row[target_attr])
    deletion_set = true_optimal(target_cell, cell_map)
    deletion_time = time.perf_counter() - deletion_start
    
    last_metrics = Metrics(query_time=query_time, graph_time=graph_time, deletion_time=deletion_time)
    return deletion_set

def run_evaluation(test_cases: List[Tuple[int, str]]):
    """Run compact performance evaluation."""
    global last_metrics
    
    print("="*80)
    print("RTF DELETION PERFORMANCE EVALUATION")
    print("="*80)
    print("Metrics: Query | Graph | Deletion | Total | Memory | Del-Set")
    print("="*80)
    
    approaches = [
        ("Multi-pass", eval_multi_pass),
        ("One-pass", eval_one_pass),
        ("True One-pass", eval_true_one_pass)
    ]
    
    all_results = []
    
    for i, (key, target_attr) in enumerate(test_cases, 1):
        print(f"\nCase {i}: key={key}, attr='{target_attr}'")
        print("-" * 50)
        
        for approach_name, eval_func in approaches:
            last_metrics = None
            metrics = measure_approach(approach_name, eval_func, key, target_attr)
            
            if last_metrics:  # Use detailed breakdown if available
                metrics.query_time = last_metrics.query_time
                metrics.graph_time = last_metrics.graph_time
                metrics.deletion_time = last_metrics.deletion_time
            
            if metrics.success:
                total = metrics.query_time + metrics.graph_time + metrics.deletion_time
                print(f"{approach_name:13} | "
                      f"{metrics.query_time:5.3f}s | "
                      f"{metrics.graph_time:5.3f}s | "
                      f"{metrics.deletion_time:8.4f}s | "
                      f"{total:5.3f}s | "
                      f"{metrics.memory_mb:5.2f}MB | "
                      f"{metrics.deletion_size:2d}")
                all_results.append((approach_name, metrics))
            else:
                print(f"{approach_name:13} | FAILED")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    by_approach = {}
    for name, metrics in all_results:
        if name not in by_approach:
            by_approach[name] = []
        by_approach[name].append(metrics)
    
    for name, metrics_list in by_approach.items():
        if not metrics_list:
            continue
            
        avg_query = sum(m.query_time for m in metrics_list) / len(metrics_list)
        avg_graph = sum(m.graph_time for m in metrics_list) / len(metrics_list)
        avg_deletion = sum(m.deletion_time for m in metrics_list) / len(metrics_list)
        avg_total = avg_query + avg_graph + avg_deletion
        avg_memory = sum(m.memory_mb for m in metrics_list) / len(metrics_list)
        avg_del_size = sum(m.deletion_size for m in metrics_list) / len(metrics_list)
        
        print(f"\n{name}:")
        print(f"  Query:    {avg_query:.4f}s ({avg_query/avg_total*100:.1f}%)")
        print(f"  Graph:    {avg_graph:.4f}s ({avg_graph/avg_total*100:.1f}%)")
        print(f"  Deletion: {avg_deletion:.4f}s ({avg_deletion/avg_total*100:.1f}%)")
        print(f"  Total:    {avg_total:.4f}s")
        print(f"  Memory:   {avg_memory:.2f}MB")
        print(f"  Del-Size: {avg_del_size:.1f}")
    
    # Performance comparison
    if len(by_approach) > 1:
        approaches = list(by_approach.keys())
        baseline = by_approach[approaches[0]]
        baseline_avg_deletion = sum(m.deletion_time for m in baseline) / len(baseline)
        
        print(f"\nDeletion Computation Speedup (vs {approaches[0]}):")
        for name in approaches[1:]:
            metrics_list = by_approach[name]
            avg_deletion = sum(m.deletion_time for m in metrics_list) / len(metrics_list)
            speedup = baseline_avg_deletion / avg_deletion if avg_deletion > 0 else float('inf')
            print(f"  {name}: {speedup:.0f}x faster")

def main():
    """Main entry point."""
    global last_metrics
    last_metrics = None
    
    # Default test cases
    test_cases = [
        (2, 'education'),
        (3, 'occupation'), 
        (4, 'workclass'),
        (5, 'relationship'),
        (1, 'age')
    ]
    
    run_evaluation(test_cases)

if __name__ == "__main__":
    main()