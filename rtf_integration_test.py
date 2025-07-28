"""
Step 1: Test your current project structure and imports
Place this file in your main RTF25 directory
"""

import sys
import os

# Test 1: Check if your directories exist
print("=== Step 1: Project Structure Check ===")

directories_to_check = [
    './RTFGraphConstruction',
    './IDcomputation', 
    './DCandDelset/dc_configs'
]

for directory in directories_to_check:
    if os.path.exists(directory):
        print(f"✓ Found: {directory}")
    else:
        print(f"✗ Missing: {directory}")

# Test 2: Check if your key files exist
files_to_check = [
    './RTFGraphConstruction/ID_graph_construction.py',
    './IDcomputation/IGC_e_get_bound_new.py',
    './cell.py'  # Assuming this exists based on your code
]

print("\n=== Key Files Check ===")
for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✓ Found: {file_path}")
    else:
        print(f"✗ Missing: {file_path}")

# Test 3: Try basic imports
print("\n=== Import Test ===")

try:
    sys.path.append('./RTFGraphConstruction')
    from ID_graph_construction import IncrementalGraphBuilder
    print("✓ Successfully imported IncrementalGraphBuilder")
except Exception as e:
    print(f"✗ Could not import IncrementalGraphBuilder: {e}")

try:
    sys.path.append('./IDcomputation')
    # Try to import your ID computation module
    import IGC_e_get_bound_new
    print("✓ Successfully imported IGC_e_get_bound_new")
except Exception as e:
    print(f"✗ Could not import IGC_e_get_bound_new: {e}")

try:
    from cell import Cell, Attribute
    print("✓ Successfully imported Cell and Attribute")
except Exception as e:
    print(f"✗ Could not import Cell/Attribute: {e}")

print("\n=== Step 1 Complete ===")
print("If you see any ✗ errors above, please fix them before proceeding to Step 2")
print("If all imports are ✓, you're ready for Step 2!")