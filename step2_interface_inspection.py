"""
Step 2: Examine your existing module interfaces
This will help us understand how to connect them properly
"""

import sys
import inspect

# Add paths
sys.path.append('./RTFGraphConstruction')
sys.path.append('./IDcomputation')

from ID_graph_construction import IncrementalGraphBuilder
import IGC_e_get_bound_new
from cell import Cell, Attribute

print("=== Step 2: Interface Inspection ===")

# Test 1: Examine IncrementalGraphBuilder
print("\n1. IncrementalGraphBuilder Analysis:")
print("   Available methods:")

# Get all methods of IncrementalGraphBuilder
builder_methods = [method for method in dir(IncrementalGraphBuilder) 
                  if not method.startswith('_') or method in ['__init__']]

for method in builder_methods:
    if hasattr(IncrementalGraphBuilder, method):
        try:
            sig = inspect.signature(getattr(IncrementalGraphBuilder, method))
            print(f"   - {method}{sig}")
        except:
            print(f"   - {method} (signature unavailable)")

# Test 2: Create a sample IncrementalGraphBuilder instance
print("\n2. Testing IncrementalGraphBuilder instantiation:")
try:
    target_info = {'key': 2, 'attribute': 'education'}
    builder = IncrementalGraphBuilder(target_info, 'adult')
    print("   ✓ Successfully created IncrementalGraphBuilder instance")
    
    # Check if it has the stub methods mentioned in your algorithm
    has_id_stub = hasattr(builder, 'id_computation_stub')
    has_check_stub = hasattr(builder, 'check_threshold_stub')
    
    print(f"   - Has id_computation_stub: {has_id_stub}")
    print(f"   - Has check_threshold_stub: {has_check_stub}")
    
except Exception as e:
    print(f"   ✗ Error creating IncrementalGraphBuilder: {e}")

# Test 3: Examine IGC_e_get_bound_new module
print("\n3. IGC_e_get_bound_new Analysis:")
print("   Available functions:")

igc_functions = [name for name in dir(IGC_e_get_bound_new) 
                if not name.startswith('_') and callable(getattr(IGC_e_get_bound_new, name))]

for func_name in igc_functions[:10]:  # Show first 10 functions
    try:
        func = getattr(IGC_e_get_bound_new, func_name)
        sig = inspect.signature(func)
        print(f"   - {func_name}{sig}")
    except:
        print(f"   - {func_name} (signature unavailable)")

if len(igc_functions) > 10:
    print(f"   ... and {len(igc_functions) - 10} more functions")

# Test 4: Check Cell and Attribute classes
print("\n4. Cell and Attribute Classes:")
try:
    # Test Cell creation
    test_attr = Attribute('adult', 'education')
    test_cell = Cell(test_attr, 2, 'Bachelors')
    print(f"   ✓ Cell created: attribute={test_cell.attribute.col}, key={test_cell.key}, value={test_cell.value}")
    
    # Check Cell methods
    cell_methods = [method for method in dir(Cell) if not method.startswith('_')]
    print(f"   - Cell methods: {cell_methods}")
    
except Exception as e:
    print(f"   ✗ Error with Cell/Attribute: {e}")

# Test 5: Check if your existing modules have any sample data
print("\n5. Sample Data Check:")
try:
    # Try to run a simple graph construction
    builder = IncrementalGraphBuilder({'key': 2, 'attribute': 'education'}, 'adult')
    
    # Check if we can call construct_full_graph
    if hasattr(builder, 'construct_full_graph'):
        print("   ✓ Found construct_full_graph method")
        print("   - This is your main graph construction method")
    else:
        print("   ✗ construct_full_graph method not found")
        
except Exception as e:
    print(f"   ✗ Error in sample data check: {e}")

print("\n=== Step 2 Complete ===")
print("Next: Step 3 will create the integration bridge between these modules")
print("\nPLEASE SHARE THIS OUTPUT so I can see your current interfaces!")