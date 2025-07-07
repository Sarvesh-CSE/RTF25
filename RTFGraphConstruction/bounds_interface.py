# File: bounds_interface.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain_operations import NumericalDomain
from IDcomputation.IGC_e_get_bound_new import DomianInferFromDC
from cell import Cell
from typing import Optional, List, Tuple

class SimpleBoundsComputer:
    """Simple interface to compute bounds for numerical cells"""
    
    def __init__(self, db_name: str = 'adult'):
        self.db_name = db_name
        self.domain_infer = DomianInferFromDC(db_name)
        print(f"Initialized bounds computer for database: {db_name}")
    
    def compute_cell_bounds(self, cell: Cell) -> Optional[NumericalDomain]:
        """Compute bounds for a single numerical cell"""
        try:
            print(f"Computing bounds for cell: {cell}")
            
            table_name = cell.attribute.table
            column_name = cell.attribute.col
            key_value = cell.key
            
            # Get target tuple
            target_tuple = self.domain_infer.get_target_tuple(table_name, 'id', key_value)
            if not target_tuple:
                print(f"  No target tuple found for key {key_value}")
                return None
            
            # Get DC list for this column
            target_dc_list = self.domain_infer.get_target_dc_list(table_name, column_name)
            if not target_dc_list:
                print(f"  No denial constraints found for column {column_name}")
                return None
            
            print(f"  Found {len(target_dc_list)} denial constraints")
            
            # Compute bounds using existing method
            bounds_list = self.domain_infer.get_bound_from_DC(
                target_dc_list=target_dc_list,
                target_tuple=target_tuple,
                table_name=table_name,
                target_column=column_name
            )
            
            if bounds_list:
                # Intersect all bounds (like bounds_simple.py)
                final_bounds = self._intersect_bounds_list(bounds_list)
                domain = NumericalDomain(final_bounds[0], final_bounds[1])
                print(f"  Computed domain: {domain}")
                return domain
            else:
                print(f"  No bounds computed")
                return None
                
        except Exception as e:
            print(f"  Error computing bounds for {cell}: {e}")
            return None
    
    def _intersect_bounds_list(self, bounds_list: List[Tuple]) -> Tuple[float, float]:
        """Intersect multiple bounds (similar to bounds_simple.py)"""
        print(f"  Intersecting {len(bounds_list)} bounds: {bounds_list}")
        
        if not bounds_list:
            return (-float('inf'), float('inf'))
        
        # Get valid bounds (not None)
        valid_bounds = [(b[0], b[1]) for b in bounds_list if b[0] is not None and b[1] is not None]
        
        if not valid_bounds:
            return (-float('inf'), float('inf'))
        
        # Intersect: max of lower bounds, min of upper bounds
        min_bound = max(b[0] for b in valid_bounds)
        max_bound = min(b[1] for b in valid_bounds)
        
        # Check if intersection is valid
        if min_bound > max_bound:
            print(f"  WARNING: Invalid intersection! Lower bound ({min_bound}) > Upper bound ({max_bound})")
            print(f"  This means no value can satisfy all constraints simultaneously")
            # Return empty domain
            return (min_bound, min_bound)  # Zero-size domain
        
        print(f"  Final intersected bounds: ({min_bound}, {max_bound})")
        return (min_bound, max_bound)

# Test this module
if __name__ == "__main__":
    from cell import Attribute, Cell
    
    # Test with a real cell
    bounds_computer = SimpleBoundsComputer('adult')
    
    print("=== Testing Different Attributes ===\n")
    
    # Test 1: Simple numerical attribute with fewer constraints
    print("1. Testing 'age' attribute:")
    attr1 = Attribute('adult_data', 'age')
    test_cell1 = Cell(attr1, key=4, value=34)
    domain1 = bounds_computer.compute_cell_bounds(test_cell1)
    
    if domain1:
        print(f"   Domain: {domain1}")
        print(f"   Size: {domain1.size()}")
        print(f"   Restriction: {domain1.restriction_level():.6f}")
    else:
        print("   Failed to compute domain")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Another numerical attribute
    print("2. Testing 'education_num' attribute:")
    attr2 = Attribute('adult_data', 'education_num')
    test_cell2 = Cell(attr2, key=4, value=9)
    domain2 = bounds_computer.compute_cell_bounds(test_cell2)
    
    if domain2:
        print(f"   Domain: {domain2}")
        print(f"   Size: {domain2.size()}")
        print(f"   Restriction: {domain2.restriction_level():.6f}")
    else:
        print("   Failed to compute domain")
        
    print("\n" + "="*50 + "\n")
    
    # Test 3: The complex fnlwgt for comparison
    print("3. Testing 'fnlwgt' attribute (complex case):")
    attr3 = Attribute('adult_data', 'fnlwgt')
    test_cell3 = Cell(attr3, key=4, value=77516)
    domain3 = bounds_computer.compute_cell_bounds(test_cell3)
    
    if domain3:
        print(f"   Domain: {domain3}")
        print(f"   Size: {domain3.size()}")
        print(f"   Restriction: {domain3.restriction_level():.6f}")
    else:
        print("   Failed to compute domain")