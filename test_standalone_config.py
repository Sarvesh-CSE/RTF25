"""
Test Standalone Config
======================
Test the complete standalone config without circular imports.
"""

print("=== Testing Standalone Config ===")

# Test 1: Basic config import
print("1. Testing basic config import...")
try:
    import config
    print("  ✓ Config imported successfully")
    
    # Test basic functions
    datasets = config.list_available_datasets()
    print(f"  ✓ Found {len(datasets)} datasets: {datasets}")
    
    # Test dataset info
    adult_info = config.get_dataset_info('adult')
    print(f"  ✓ Adult dataset info: {adult_info['primary_table']}")
    
    # Test domain file path (this was missing before)
    domain_path = config.get_domain_file_path('adult')
    print(f"  ✓ Domain file path: {domain_path}")
    
except Exception as e:
    print(f"  ✗ Config import failed: {e}")

# Test 2: Cell import
print("\n2. Testing cell import...")
try:
    from cell import Cell, Attribute
    
    attr = Attribute('adult', 'education')
    cell = Cell(attr, 2, 'Bachelors')
    print(f"  ✓ Cell system: {cell.attribute.col} = {cell.value}")
    
except Exception as e:
    print(f"  ✗ Cell import failed: {e}")

# Test 3: Graph construction
print("\n3. Testing graph construction...")
try:
    import sys
    import os
    sys.path.append(os.path.join(os.getcwd(), 'RTFGraphConstruction'))
    
    from RTFGraphConstruction.ID_graph_construction import IncrementalGraphBuilder
    
    target_info = {'key': 2, 'attribute': 'education'}
    builder = IncrementalGraphBuilder(target_info, 'adult')
    print("  ✓ IncrementalGraphBuilder initialized")
    
except Exception as e:
    print(f"  ✗ Graph construction failed: {e}")

# Test 4: ID computation
print("\n4. Testing ID computation...")
try:
    sys.path.append(os.path.join(os.getcwd(), 'IDcomputation'))
    
    from IDcomputation.IGC_e_get_bound_new import AttributeDomainComputation
    
    domain_comp = AttributeDomainComputation('adult')
    print("  ✓ AttributeDomainComputation initialized")
    
    # Try to get domain
    try:
        domain_info = domain_comp.get_domain('adult_data', 'education')
        if domain_info and 'values' in domain_info:
            print(f"  ✓ Domain retrieved: {len(domain_info['values'])} education values")
        else:
            print("  - Domain computation works but no data available")
    except Exception as domain_e:
        print(f"  - Domain computation initialized but data access failed: {domain_e}")
    
except Exception as e:
    print(f"  ✗ ID computation failed: {e}")

print("\n=== Standalone Config Test Complete ===")
print("If all components show ✓, the config fix is working!")
