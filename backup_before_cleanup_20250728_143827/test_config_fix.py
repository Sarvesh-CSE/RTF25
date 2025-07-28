"""
Test Config Import Fix
======================
Test that config imports work after the fix.
"""

import sys
import os

print("=== Testing Config Import Fix ===")

# Test 1: Direct config import (should use compatibility layer)
print("1. Testing direct config import...")
try:
    import config
    print("  ✓ import config successful")
    
    if hasattr(config, 'get_dataset_info'):
        datasets = config.list_available_datasets()
        print(f"  ✓ Found datasets: {datasets}")
    else:
        print("  - Config imported but functions not available")
        
except Exception as e:
    print(f"  ✗ import config failed: {e}")

# Test 2: rtf_core.config import
print("\n2. Testing rtf_core.config import...")
try:
    from rtf_core.config import get_dataset_info, list_available_datasets
    print("  ✓ rtf_core.config import successful")
    
    datasets = list_available_datasets()
    print(f"  ✓ rtf_core.config datasets: {datasets}")
    
except Exception as e:
    print(f"  ✗ rtf_core.config import failed: {e}")

# Test 3: Cell import (should work now)
print("\n3. Testing cell import...")
try:
    from cell import Cell, Attribute
    print("  ✓ Cell import successful")
    
    attr = Attribute('adult', 'education')
    cell = Cell(attr, 2, 'Bachelors')
    print(f"  ✓ Cell creation: {cell.attribute.col} = {cell.value}")
    
except Exception as e:
    print(f"  ✗ Cell import failed: {e}")

# Test 4: Graph construction (should work now)
print("\n4. Testing graph construction...")
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'RTFGraphConstruction'))
    from RTFGraphConstruction.ID_graph_construction import IncrementalGraphBuilder
    print("  ✓ IncrementalGraphBuilder import successful")
    
    builder = IncrementalGraphBuilder({'key': 2, 'attribute': 'education'}, 'adult')
    print("  ✓ IncrementalGraphBuilder initialization successful")
    
except Exception as e:
    print(f"  ✗ Graph construction failed: {e}")

# Test 5: ID computation (should work now)
print("\n5. Testing ID computation...")
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'IDcomputation'))
    from IDcomputation.IGC_e_get_bound_new import AttributeDomainComputation
    print("  ✓ AttributeDomainComputation import successful")
    
    domain_comp = AttributeDomainComputation('adult')
    print("  ✓ AttributeDomainComputation initialization successful")
    
except Exception as e:
    print(f"  ✗ ID computation failed: {e}")

print("\n=== Config Import Test Complete ===")
print("If all tests show ✓, the config import fix is working!")
