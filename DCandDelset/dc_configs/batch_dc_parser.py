import re
import os

def parse_denial_constraints_from_file(input_file):
    """Parse denial constraints from a raw constraint file."""
    operator_map = {'<>': '!=', '==': '==', '>': '>', '<': '<', '>=': '>=', '<=': '<='}
    # Enhanced pattern to handle hyphens and underscores in attribute names
    pattern = re.compile(r'(t1\.[\w\-_]+|t2\.[\w\-_]+)\s*(<>|==|>=|<=|>|<)\s*(t1\.[\w\-_]+|t2\.[\w\-_]+)')
    parsed_dcs = []

    try:
        with open(input_file, "r", encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or not line.startswith("not"):
                    continue
                
                predicates = pattern.findall(line)
                if predicates:
                    parsed = [(lhs, operator_map.get(op, op), rhs) for lhs, op, rhs in predicates]
                    parsed_dcs.append(parsed)
                else:
                    print(f"Warning: Could not parse line {line_num}: {line}")
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return []

    return parsed_dcs

def write_parsed_dcs_to_file(denial_constraints, output_file, dataset_name):
    """Write the parsed DCs to a Python file as a denial_constraints variable."""
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(f"# Parsed denial constraints for {dataset_name}\n")
        f.write(f"# Generated automatically from raw constraints\n\n")
        f.write("denial_constraints = [\n")
        for dc in denial_constraints:
            f.write(f"    {dc},\n")
        f.write("]\n")
    
    print(f"✓ Parsed {len(denial_constraints)} denial constraints for {dataset_name}")

def batch_parse_all_dcs():
    """Parse all DC files in the raw_constraints directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_constraints_dir = os.path.join(script_dir, "raw_constraints")
    
    if not os.path.exists(raw_constraints_dir):
        print(f"Error: Directory {raw_constraints_dir} does not exist")
        return
    
    # Get all files in raw_constraints directory
    raw_files = [f for f in os.listdir(raw_constraints_dir) if os.path.isfile(os.path.join(raw_constraints_dir, f))]
    
    if not raw_files:
        print(f"No files found in {raw_constraints_dir}")
        return
    
    print(f"Found {len(raw_files)} files in raw_constraints:")
    for f in raw_files:
        print(f"  - {f}")
    
    print("\nProcessing files...")
    
    successful_parses = 0
    total_constraints = 0
    
    for raw_file in raw_files:
        input_path = os.path.join(raw_constraints_dir, raw_file)
        
        # Generate output filename: topAdultDCs -> topAdultDCs_parsed.py
        output_filename = f"{raw_file}_parsed.py"
        output_path = os.path.join(script_dir, output_filename)
        
        # Extract dataset name for documentation
        dataset_name = raw_file.replace("top", "").replace("DCs", "")
        if not dataset_name:
            dataset_name = raw_file
        
        print(f"\nProcessing: {raw_file}")
        
        # Parse the constraints
        dcs = parse_denial_constraints_from_file(input_path)
        
        if dcs:
            write_parsed_dcs_to_file(dcs, output_path, dataset_name)
            successful_parses += 1
            total_constraints += len(dcs)
        else:
            print(f"✗ No constraints found or error parsing {raw_file}")
    
    print(f"\n" + "="*50)
    print(f"Summary:")
    print(f"Files processed: {len(raw_files)}")
    print(f"Successful parses: {successful_parses}")
    print(f"Total constraints parsed: {total_constraints}")
    print(f"Generated files saved in: {script_dir}")

if __name__ == "__main__":
    batch_parse_all_dcs()