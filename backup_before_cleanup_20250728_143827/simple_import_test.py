"""
Simple Import Test
==================
Test individual components step by step.
"""

import sys
import os

print("=== Simple Import Diagnostic ===")

# Add paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

print("1. Testing rtf_core.config import...")
try:
    from rtf_core.config import get_dataset_info, list_available_datasets
    print("  ✓ rtf_core.config imported successfully")
    
    datasets = list_available_datasets()
    print(f"  ✓ Found datasets: {datasets}")
except Exception as e:
    print(f"  ✗ Config import failed: {e}")

print("\n2. Testing cell.py import...")
try:
    from cell import Cell, Attribute
    print("  ✓ Cell and Attribute imported successfully")
    
    attr = Attribute('adult', 'education')
    cell = Cell(attr, 2, 'Bachelors')
    print(f"  ✓ Cell creation: {cell.attribute.col} = {cell.value}")
except Exception as e:
    print(f"  ✗ Cell import failed: {e}")

print("\n3. Testing graph construction...")
try:
    sys.path.append(os.path.join(project_root, 'RTFGraphConstruction'))
    from RTFGraphConstruction.ID_graph_construction import IncrementalGraphBuilder
    print("  ✓ IncrementalGraphBuilder imported")
    
    builder = IncrementalGraphBuilder({'key': 2, 'attribute': 'education'}, 'adult')
    print("  ✓ IncrementalGraphBuilder initialized")
except Exception as e:
    print(f"  ✗ Graph construction failed: {e}")

print("\n4. Testing ID computation...")
try:
    sys.path.append(os.path.join(project_root, 'IDcomputation'))
    from IDcomputation.IGC_e_get_bound_new import AttributeDomainComputation
    print("  ✓ AttributeDomainComputation imported")
    
    domain_comp = AttributeDomainComputation('adult')
    print("  ✓ AttributeDomainComputation initialized")
except Exception as e:
    print(f"  ✗ ID computation failed: {e}")

print("\n=== Test Complete ===")
print("If all components work individually, we can create a working optimizer.")
