"""
Step 4b: Debug the exact signature of your domain computation methods
"""

import sys
import inspect
sys.path.append('./IDcomputation')

from IGC_e_get_bound_new import AttributeDomainComputation

print("=== Step 4b: Domain Method Debugging ===")

# Create an instance
domain_computer = AttributeDomainComputation('adult')

# Check the exact signature of get_domain method
print("1. Checking get_domain method signature:")
try:
    sig = inspect.signature(domain_computer.get_domain)
    print(f"   get_domain signature: {sig}")
    
    # Get parameter names
    params = list(sig.parameters.keys())
    print(f"   Parameters: {params}")
    
except Exception as e:
    print(f"   Error getting signature: {e}")

# Check what methods are available
print("\n2. Available methods in AttributeDomainComputation:")
methods = [method for method in dir(domain_computer) if not method.startswith('_')]
for method in methods:
    print(f"   - {method}")

# Try different ways to call get_domain
print("\n3. Testing different get_domain calls:")

test_calls = [
    # Test 1: Just column
    ("domain_computer.get_domain('education')", 
     lambda: domain_computer.get_domain('education')),
    
    # Test 2: Column with table
    ("domain_computer.get_domain('adult_data', 'education')", 
     lambda: domain_computer.get_domain('adult_data', 'education')),
    
    # Test 3: Table and column as keywords  
    ("domain_computer.get_domain(table='adult_data', column='education')", 
     lambda: domain_computer.get_domain(table='adult_data', column='education')),
    
    # Test 4: Just column as keyword
    ("domain_computer.get_domain(column='education')", 
     lambda: domain_computer.get_domain(column='education')),
]

for test_name, test_func in test_calls:
    try:
        print(f"   Trying: {test_name}")
        result = test_func()
        print(f"   ✓ Success! Result: {result}")
        print(f"   Result type: {type(result)}")
        if hasattr(result, '__len__'):
            print(f"   Result length: {len(result)}")
        break  # Stop on first success
    except Exception as e:
        print(f"   ✗ Failed: {e}")

print("\n=== Next: I'll use the working method call in Step 5 ===")