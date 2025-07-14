#!/usr/bin/env python3
"""
Modular Build Hyperedges - Dataset-Agnostic Hyperedge Generation
===============================================================

Step-by-step modular refactoring:
1. Use config.py for dataset configuration
2. Use fetch_row.py for database operations  
3. Support any dataset and DC configuration
4. Clean separation of concerns

Usage:
    from build_hyperedges import HyperedgeBuilder
    
    # For any dataset
    builder = HyperedgeBuilder('adult')
    hyperedge_map = builder.build_hyperedge_map(target_key=2, target_attr='education')
    
    # For different datasets
    tax_builder = HyperedgeBuilder('tax')
    hospital_builder = HyperedgeBuilder('hospital')
"""

import sys
import os
from typing import Any, Dict, List, Set, Optional
from importlib import import_module

# Add project root for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modular components
from cell import Attribute, Cell, Hyperedge
from config import get_dataset_info, list_available_datasets
from fetch_row import RTFDatabaseManager


class HyperedgeBuilder:
    """Modular hyperedge builder supporting any dataset."""
    
    def __init__(self, dataset: str):
        """
        Initialize hyperedge builder for specific dataset.
        
        Args:
            dataset: Dataset name from config.py ('adult', 'tax', 'hospital', etc.)
        """
        self.dataset = dataset
        self.dataset_info = get_dataset_info(dataset)
        self.primary_table = self.dataset_info['primary_table']
        self.denial_constraints = self._load_denial_constraints()
        
        print(f"HyperedgeBuilder initialized for dataset: {dataset}")
        print(f"  Primary table: {self.primary_table}")
        print(f"  DC constraints: {len(self.denial_constraints)}")
    
    def _load_denial_constraints(self) -> List:
        """Load denial constraints for this dataset."""
        try:
            # Get DC module path from config
            dc_module_path = self.dataset_info.get('dc_config_module')
            if not dc_module_path:
                print(f"Warning: No DC config module specified for {self.dataset}")
                return []
            
            # Import the DC module dynamically
            dc_module = import_module(dc_module_path)
            denial_constraints = getattr(dc_module, 'denial_constraints', [])
            
            return denial_constraints
            
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not load denial constraints for {self.dataset}: {e}")
            return []
    
    def build_hyperedges(self, row: Dict[str, Any], key: Any, target_attr: str) -> List[Hyperedge]:
        """
        Build hyperedges for a specific target attribute.
        
        Args:
            row: Database row as dictionary
            key: Primary key value
            target_attr: Target attribute name
            
        Returns:
            List of hyperedges where target_attr is the head
        """
        if not self.denial_constraints:
            print(f"Warning: No denial constraints available for {self.dataset}")
            return []
        
        seen: Dict[frozenset, Hyperedge] = {}
        
        for dc in self.denial_constraints:
            head_idx = self._find_target_predicate(dc, target_attr)
            if head_idx is None:
                continue
            
            # All other predicates become the tail
            tail_preds = [pred for j, pred in enumerate(dc) if j != head_idx]
            cells = self._create_tail_cells(tail_preds, row, key)
            
            if cells:  # Only create hyperedge if we have tail cells
                he = Hyperedge(cells)
                keyset = frozenset(he)
                if keyset not in seen:
                    seen[keyset] = he
        
        return list(seen.values())
    
    def _find_target_predicate(self, dc: List, target_attr: str) -> Optional[int]:
        """Find which predicate in DC contains the target attribute."""
        for i, (left, _, right) in enumerate(dc):
            left_col = left.split('.')[-1]  # Handle table.column format
            right_col = right.split('.')[-1]
            if left_col == target_attr or right_col == target_attr:
                return i
        return None
    
    def _create_tail_cells(self, tail_preds: List, row: Dict[str, Any], key: Any) -> List[Cell]:
        """Create Cell objects for tail predicates."""
        cells = []
        for (left, _, _) in tail_preds:
            col = left.split('.')[-1]  # Extract column name
            if col in row:  # Check if column exists in row
                value = row[col]
                attr = Attribute(self.primary_table, col)
                cells.append(Cell(attr, key, value))
        return cells
    
    def build_hyperedge_map(self, target_key: int, start_attr: str, 
                           db_manager: Optional[RTFDatabaseManager] = None) -> Dict[Cell, List[Hyperedge]]:
        """
        Build complete hyperedge map starting from target attribute.
        
        Args:
            target_key: Primary key of target row
            start_attr: Starting attribute name
            db_manager: Optional database manager (will create if None)
            
        Returns:
            Dictionary mapping cells to their hyperedges
        """
        # Get the row data
        if db_manager:
            row = db_manager.fetch_row(target_key)
            close_connection = False
        else:
            db_manager = RTFDatabaseManager(self.dataset)
            db_manager.__enter__()
            row = db_manager.fetch_row(target_key)
            close_connection = True
        
        try:
            # Create all cells for this row
            all_cells: Dict[str, Cell] = {}
            for col_name, val in row.items():
                attr = Attribute(self.primary_table, col_name)
                all_cells[col_name] = Cell(attr, target_key, val)
            
            # Initialize hyperedge map
            hyperedge_map: Dict[Cell, List[Hyperedge]] = {
                cell: [] for cell in all_cells.values()
            }
            
            # BFS traversal to build hyperedge map
            visited_attrs: Set[str] = {start_attr}
            frontier: List[str] = [start_attr]
            
            while frontier:
                next_frontier: List[str] = []
                
                for target_attr in frontier:
                    head_cell = all_cells[target_attr]
                    hyperedges = self.build_hyperedges(row, target_key, target_attr)
                    
                    for he in hyperedges:
                        hyperedge_map[head_cell].append(he)
                        
                        # Add unvisited tail cells to frontier
                        for tail_cell in he:
                            col = tail_cell.attribute.col
                            if col not in visited_attrs:
                                visited_attrs.add(col)
                                next_frontier.append(col)
                
                frontier = next_frontier
            
            return hyperedge_map
            
        finally:
            if close_connection:
                db_manager.__exit__(None, None, None)
    
    def print_hyperedge_summary(self, hyperedge_map: Dict[Cell, List[Hyperedge]]) -> None:
        """Print summary of hyperedge map."""
        print(f"\n=== Hyperedge Map Summary for {self.dataset} ===")
        
        total_hyperedges = sum(len(hes) for hes in hyperedge_map.values())
        cells_with_hyperedges = sum(1 for hes in hyperedge_map.values() if hes)
        
        print(f"Total cells: {len(hyperedge_map)}")
        print(f"Cells with hyperedges: {cells_with_hyperedges}")
        print(f"Total hyperedges: {total_hyperedges}")
        
        # Show detailed breakdown
        print(f"\nDetailed breakdown:")
        for head_cell, hyperedges in hyperedge_map.items():
            if hyperedges:
                print(f"  {head_cell.attribute.col}: {len(hyperedges)} hyperedges")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def build_hyperedges_for_dataset(dataset: str, target_key: int, target_attr: str) -> Dict[Cell, List[Hyperedge]]:
    """
    Convenience function to build hyperedges for any dataset.
    
    Args:
        dataset: Dataset name ('adult', 'tax', 'hospital', etc.)
        target_key: Primary key value
        target_attr: Target attribute name
        
    Returns:
        Hyperedge map
    """
    builder = HyperedgeBuilder(dataset)
    return builder.build_hyperedge_map(target_key, target_attr)


def quick_hyperedge_test(dataset: str = 'adult', target_key: int = 2, target_attr: str = 'education'):
    """Quick test function for any dataset."""
    print(f"Quick hyperedge test: {dataset}, key={target_key}, attr={target_attr}")
    
    try:
        builder = HyperedgeBuilder(dataset)
        hyperedge_map = builder.build_hyperedge_map(target_key, target_attr)
        builder.print_hyperedge_summary(hyperedge_map)
        return hyperedge_map
        
    except Exception as e:
        print(f"Error testing {dataset}: {e}")
        return None


# ============================================================================
# TESTING AND DEMO
# ============================================================================

if __name__ == "__main__":
    print("Modular Hyperedge Builder Demo")
    print("=" * 40)
    
    # Test with different datasets
    datasets_to_test = ['adult', 'tax', 'hospital']
    
    for dataset in datasets_to_test:
        try:
            print(f"\n--- Testing {dataset} dataset ---")
            
            # Test if dataset is available
            available_datasets = list_available_datasets()
            if dataset not in available_datasets:
                print(f"Dataset {dataset} not available. Available: {available_datasets}")
                continue
            
            # Build hyperedges
            builder = HyperedgeBuilder(dataset)
            
            # Use database manager for efficient connection handling
            with RTFDatabaseManager(dataset) as db_manager:
                hyperedge_map = builder.build_hyperedge_map(
                    target_key=2, 
                    start_attr='education' if dataset == 'adult' else 'salary',  # Different attrs for different datasets
                    db_manager=db_manager
                )
                
                builder.print_hyperedge_summary(hyperedge_map)
            
        except Exception as e:
            print(f"Error with {dataset}: {e}")
    
    print(f"\nModular hyperedge builder demo completed!")