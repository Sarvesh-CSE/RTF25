import re
import os

def parse_denial_constraints_from_file(input_file):
    operator_map = {'<>': '!=', '==': '==', '>': '>', '<': '<'}
    # Allow hyphens in attribute names
    pattern = re.compile(r'(t1\.[\w\-]+|t2\.[\w\-]+)\s*(<>|==|<|>)\s*(t1\.[\w\-]+|t2\.[\w\-]+)')
    parsed_dcs = []

    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or not line.startswith("not"):
                continue
            predicates = pattern.findall(line)
            parsed = [(lhs, operator_map[op], rhs) for lhs, op, rhs in predicates]
            parsed_dcs.append(parsed)

    return parsed_dcs

def write_parsed_dcs_to_file(denial_constraints, output_file):
    """
    Writes the parsed DCs to a Python file as a denial_constraints variable.
    """
    with open(output_file, "w") as f:
        f.write("denial_constraints = [\n")
        for dc in denial_constraints:
            f.write(f"    {dc},\n")
        f.write("]\n")
    print(f"Parsed {len(denial_constraints)} denial constraints and saved to {output_file}")

if __name__ == "__main__":
    input_file = "topAdultDCs"       # Rename to 'topAdultDCs.txt' if needed
    output_file = f"{input_file}_parsed.py"
    
    dcs = parse_denial_constraints_from_file(input_file)
    write_parsed_dcs_to_file(dcs, output_file)
