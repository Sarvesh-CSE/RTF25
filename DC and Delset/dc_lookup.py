import pandas as pd
import argparse


# This script will look into the DCs at the attribute level.
# For each attribute, a set of DCs are generated. Only these DCs are used for further graph generation for a given cell associated with some attribute.

def load_dc_config(db_name):
    """
    Load denial constraints from the appropriate config module based on the database name.
    """
    db_name = db_name.lower()
    if db_name == "rtf25":
        from dc_configs import rtf25_dcs as dc_config
    elif db_name == "tpchdb":
        from dc_configs import tpch_dcs as dc_config
    elif db_name == "adult":
        from dc_configs import topAdultDCs_parsed as dc_config
    else:
        raise ValueError(f"Unsupported DB: {db_name}")
    
    return dc_config.denial_constraints

def normalize(attr):
    return attr.split(".")[1] if "." in attr else attr

def generate_lookup_table_from_dc_list(dc_list):
    """
    Generates a lookup table mapping normalized attributes to DC labels (ϕi).
    Logs any malformed predicates skipped during processing.
    """
    lookup_table = {}

    for idx, dc in enumerate(dc_list):
        dc_label = f"ϕ{idx + 1}"
        for predicate in dc:
            if isinstance(predicate, (list, tuple)) and len(predicate) == 3:
                lhs, _, rhs = predicate
                for attr in (lhs, rhs):
                    key = normalize(attr)
                    if key not in lookup_table:
                        lookup_table[key] = set()
                    lookup_table[key].add(dc_label)
            else:
                print(f"Skipped malformed predicate in {dc_label}: {predicate}")

    return lookup_table

def print_lookup_table(lookup_table):
    for attr, dcs in lookup_table.items():
        print(f"Attribute: {attr}, Denial Constraints: {', '.join(dcs)}")

def main():
    parser = argparse.ArgumentParser(description='Generate denial constraint lookup table')
    parser.add_argument('--db', '--database', 
                      default='adult',
                      help='Database name (default: rtf25)')
    
    args = parser.parse_args()
    denial_constraints = load_dc_config(args.db)
    if not denial_constraints:
        print(f"No denial constraints found for database '{args.db}'.")
        return
    
    lookup = generate_lookup_table_from_dc_list(denial_constraints)
    print(f"Denial Constraint Lookup Table for '{args.db}':\n")
    print_lookup_table(lookup)

if __name__ == "__main__":
    main()

# lookup_table = generate_lookup_table_from_dc_list()
# print_lookup_table(lookup_table)
# The output will show the attributes and the corresponding denial constraints associated with them.
# This lookup table can be used to quickly identify which denial constraints are relevant for a given attribute.
