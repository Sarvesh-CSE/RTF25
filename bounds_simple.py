#!/usr/bin/env python3
"""
Bounds Integration - Working version with fallbacks
"""

from cell import Cell, Attribute
from IDcomputation.IGC_e_get_bound_new import DomianInferFromDC


def get_restriction(cell: Cell) -> float:
    """Get restriction level for numerical attributes only (smaller = more restrictive)"""
    numerical_attrs = {'age', 'fnlwgt', 'education_num', 'capital_gain', 'capital_loss', 'hours_per_week'}
    
    if cell.attribute.col not in numerical_attrs:
        raise NotImplementedError(f"Categorical attribute '{cell.attribute.col}' not supported yet")
    
    # First try DC-based bounds computation
    try:
        domain_infer = DomianInferFromDC()
        tuple_data = domain_infer.get_target_tuple('adult_data', 'id', cell.key)
        dc_list = domain_infer.get_target_dc_list('adult_data', cell.attribute.col)
        
        if tuple_data and dc_list:
            bounds = domain_infer.get_bound_from_DC(
                target_dc_list=dc_list, target_tuple=tuple_data,
                target_column=cell.attribute.col, table_name='adult_data'
            )
            if bounds:
                min_range = float('inf')
                for pair in bounds:
                    if len(pair) == 2 and None not in pair:
                        min_range = min(min_range, abs(pair[1] - pair[0]))
                
                if min_range != float('inf'):
                    print(f"[OK] DC bounds found for {cell.attribute.col}: {min_range}")
                    return min_range
    except Exception as e:
        print(f"? DC bounds failed for {cell.attribute.col}: {e}")
    
    # Fallback to default restrictions
    print(f"-> Using default restriction for {cell.attribute.col}")
    return _get_default_restriction(cell)


def _get_default_restriction(cell: Cell) -> float:
    """Default restriction levels based on typical adult dataset ranges"""
    defaults = {
        'age': 20.0,           # 0-100 range, moderate restriction
        'fnlwgt': 50000.0,     # Very large range, less restrictive  
        'education_num': 5.0,  # 1-16 range, more restrictive
        'capital_gain': 1000.0,# Wide variation
        'capital_loss': 500.0, # Smaller range
        'hours_per_week': 15.0 # 1-99 range, moderate restriction
    }
    return defaults.get(cell.attribute.col, 100.0)


def test_all_numerical_attrs():
    """Test restriction computation for all numerical attributes"""
    from InferenceGraph.bulid_hyperedges import fetch_row
    
    row = fetch_row(2)
    numerical_attrs = ['age', 'fnlwgt', 'education_num', 'capital_gain', 'capital_loss', 'hours_per_week']
    
    print("Testing restriction computation for all numerical attributes:")
    print("=" * 60)
    
    for attr in numerical_attrs:
        try:
            cell = Cell(Attribute('adult_data', attr), 2, row[attr])
            restriction = get_restriction(cell)
            print(f"{attr:15} (value={row[attr]:>8}): restriction = {restriction:>8.1f}")
        except Exception as e:
            print(f"{attr:15}: ERROR - {e}")


if __name__ == "__main__":
    # Test single attribute
    from InferenceGraph.bulid_hyperedges import fetch_row
    
    row = fetch_row(2)
    cell = Cell(Attribute('adult_data', 'age'), 2, row['age'])
    restriction = get_restriction(cell)
    print(f"\nAge restriction: {restriction}")
    
    print("\n" + "="*60)
    
    # Test all numerical attributes
    test_all_numerical_attrs()