#!/usr/bin/env python3
"""
Compact Modular Hyperedge Builder
=================================

Usage:
    from build_hyperedges import HyperedgeBuilder
    
    builder = HyperedgeBuilder('adult')
    with RTFDatabaseManager('adult') as db:
        row = db.fetch_row(2)
        hyperedge_map = builder.build_hyperedge_map(row, 2, 'education')
"""

import sys
import os
from typing import Any, Dict, List
from importlib import import_module

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cell import Attribute, Cell, Hyperedge
from config import get_dataset_info, list_available_datasets
from fetch_row import RTFDatabaseManager


class HyperedgeBuilder:
    """Compact hyperedge builder for any dataset."""
    
    def __init__(self, dataset: str):
        self.dataset = dataset
        self.dataset_info = get_dataset_info(dataset)
        self.primary_table = self.dataset_info['primary_table']
        self.denial_constraints = self._load_dcs()
    
    def _load_dcs(self) -> List:
        """Load denial constraints for dataset."""
        try:
            dc_module_path = self.dataset_info.get('dc_config_module')
            if dc_module_path:
                dc_module = import_module(dc_module_path)
                return getattr(dc_module, 'denial_constraints', [])
        except:
            pass
        return []
    
    def build_hyperedges(self, row: Dict[str, Any], key: Any, target_attr: str) -> List[Hyperedge]:
        """Build hyperedges for target attribute."""
        if not self.denial_constraints:
            return []
        
        seen = {}
        
        for dc in self.denial_constraints:
            head_idx = None
            for i, (left, _, right) in enumerate(dc):
                left_col = left.split('.')[-1]
                right_col = right.split('.')[-1]
                if left_col == target_attr or right_col == target_attr:
                    head_idx = i
                    break
            
            if head_idx is None:
                continue
            
            tail_preds = [pred for j, pred in enumerate(dc) if j != head_idx]
            cells = []
            for (left, _, _) in tail_preds:
                col = left.split('.')[-1]
                if col in row:
                    cells.append(Cell(Attribute(self.primary_table, col), key, row[col]))
            
            if cells:
                he = Hyperedge(cells)
                keyset = frozenset(he)
                seen[keyset] = he
        
        return list(seen.values())
    
    def build_hyperedge_map(self, row: Dict[str, Any], target_key: int, start_attr: str) -> Dict[Cell, List[Hyperedge]]:
        """Build complete hyperedge map from row data."""
        # Create all cells
        all_cells = {col: Cell(Attribute(self.primary_table, col), target_key, val) 
                    for col, val in row.items()}
        
        # Initialize hyperedge map
        hyperedge_map = {cell: [] for cell in all_cells.values()}
        
        # BFS traversal
        visited = {start_attr}
        frontier = [start_attr]
        
        while frontier:
            next_frontier = []
            for target_attr in frontier:
                head_cell = all_cells[target_attr]
                hyperedges = self.build_hyperedges(row, target_key, target_attr)
                
                for he in hyperedges:
                    hyperedge_map[head_cell].append(he)
                    for tail_cell in he:
                        col = tail_cell.attribute.col
                        if col not in visited:
                            visited.add(col)
                            next_frontier.append(col)
            
            frontier = next_frontier
        
        return hyperedge_map

if __name__ == "__main__":
    print("Compact Hyperedge Builder Test")
    print("=" * 35)
    
    # Test with different datasets using config test_attribute
    test_datasets = ['adult'] # , 'tax', 'hospital'
    
    for dataset in test_datasets:
        try:
            print(f"\n--- Testing {dataset} ---")
            
            # Check if dataset available
            available_datasets = list_available_datasets()
            if dataset not in available_datasets:
                print(f"Dataset not available. Available: {available_datasets}")
                continue
            
            builder = HyperedgeBuilder(dataset)
            test_attr = builder.dataset_info.get('test_attribute', 'education')
            
            with RTFDatabaseManager(dataset) as db_manager:
                row = db_manager.fetch_row(2)
                hyperedge_map = builder.build_hyperedge_map(row, 2, test_attr)
            
            total = sum(len(hes) for hes in hyperedge_map.values())
            print(f"  Test attribute: {test_attr}")
            print(f"  Total hyperedges: {total}")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nTest completed!")