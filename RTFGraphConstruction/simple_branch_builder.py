# File: simple_branch_builder.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain_operations import NumericalDomain
from bounds_interface import SimpleBoundsComputer
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row
from cell import Attribute, Cell, Hyperedge
from typing import List, Optional

class SimpleBranchBuilder:
    """Very simple branch builder - one branch at a time"""
    
    def __init__(self, target_cell: Cell):
        self.target_cell = target_cell
        self.bounds_computer = SimpleBoundsComputer('adult')
        self.cell_domains = {}  # cell -> domain
        
        print(f"Simple branch builder for: {target_cell}")
    
    def build_one_branch(self, max_depth: int = 3) -> List[Cell]:
        """Build just ONE complete branch"""
        print(f"\n=== Building One Branch (max depth {max_depth}) ===")
        
        # Step 1: Get first cell (most restricted from target's hyperedges)
        first_cell = self._get_first_cell()
        if not first_cell:
            print("No first cell found")
            return []
        
        # Step 2: Build branch from first cell
        branch = [first_cell]
        current_cell = first_cell
        
        for depth in range(1, max_depth):
            print(f"\nDepth {depth}: Looking from {current_cell}")
            next_cell = self._get_next_cell(current_cell, branch)
            
            if next_cell:
                branch.append(next_cell)
                current_cell = next_cell
                print(f"  Added: {next_cell}")
            else:
                print(f"  No next cell - branch complete at depth {depth}")
                break
        
        print(f"\nBranch complete with {len(branch)} cells")
        self._print_branch(branch)
        return branch
    
    def _get_first_cell(self) -> Optional[Cell]:
        """Get the most restricted cell from target's hyperedges"""
        print("Finding first cell...")
        
        # Get target's hyperedges
        row = fetch_row(self.target_cell.key)
        target_attr = self.target_cell.attribute.col
        hyperedge_map = build_hyperedge_map(row, self.target_cell.key, target_attr)
        hyperedges = hyperedge_map.get(self.target_cell, [])
        
        print(f"Target has {len(hyperedges)} hyperedges")
        
        # Find all numerical cells
        candidates = []
        for he in hyperedges:
            for cell in he:
                if self._is_numerical(cell) and cell != self.target_cell:
                    candidates.append(cell)
        
        print(f"Found {len(candidates)} candidate cells")
        
        # Compute domains and find most restricted
        best_cell = None
        best_restriction = 0
        
        for cell in candidates:
            domain = self.bounds_computer.compute_cell_bounds(cell)
            if domain:
                self.cell_domains[cell] = domain
                restriction = domain.restriction_level()
                print(f"  {cell}: restriction = {restriction:.4f}")
                
                if restriction > best_restriction:
                    best_restriction = restriction
                    best_cell = cell
        
        if best_cell:
            print(f"First cell: {best_cell} (restriction: {best_restriction:.4f})")
        
        return best_cell
    
    def _get_next_cell(self, current_cell: Cell, branch: List[Cell]) -> Optional[Cell]:
        """Get next cell in the branch"""
        # Get current cell's hyperedges
        row = fetch_row(current_cell.key)
        cell_attr = current_cell.attribute.col
        hyperedge_map = build_hyperedge_map(row, current_cell.key, cell_attr)
        hyperedges = hyperedge_map.get(current_cell, [])
        
        print(f"  Current cell has {len(hyperedges)} hyperedges")
        
        # Find candidates
        candidates = []
        for he in hyperedges:
            for cell in he:
                if (self._is_numerical(cell) and 
                    cell != self.target_cell and 
                    cell not in branch):  # Avoid cycles
                    candidates.append(cell)
        
        print(f"  Found {len(candidates)} new candidates")
        
        if not candidates:
            return None
        
        # Compute domains and find most restricted
        best_cell = None
        best_restriction = 0
        
        for cell in candidates:
            if cell not in self.cell_domains:
                domain = self.bounds_computer.compute_cell_bounds(cell)
                if domain:
                    self.cell_domains[cell] = domain
            
            if cell in self.cell_domains:
                restriction = self.cell_domains[cell].restriction_level()
                if restriction > best_restriction:
                    best_restriction = restriction
                    best_cell = cell
        
        return best_cell
    
    def _is_numerical(self, cell: Cell) -> bool:
        """Check if cell is numerical"""
        try:
            float(cell.value)
            return True
        except:
            return False
    
    def _print_branch(self, branch: List[Cell]):
        """Print the branch nicely"""
        print(f"\n=== Branch Summary ===")
        for i, cell in enumerate(branch, 1):
            if cell in self.cell_domains:
                domain = self.cell_domains[cell]
                print(f"{i}. {cell}")
                print(f"   Domain: {domain}")
                print(f"   Restriction: {domain.restriction_level():.4f}")

# Test this simple version
if __name__ == "__main__":
    from cell import Attribute, Cell
    
    # Test with age attribute
    attr = Attribute('adult_data', 'age')
    target_cell = Cell(attr, key=4, value=34)
    
    # Build one branch
    builder = SimpleBranchBuilder(target_cell)
    branch = builder.build_one_branch(max_depth=3)
    
    print(f"\n=== Results ===")
    print(f"Built branch with {len(branch)} cells")
    
    if branch:
        print("Deletion order (follow this branch):")
        for i, cell in enumerate(branch, 1):
            print(f"  {i}. Delete {cell}")