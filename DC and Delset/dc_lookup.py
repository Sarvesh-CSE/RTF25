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
    else:
        raise ValueError(f"Unsupported DB: {db_name}")
    
    return dc_config.denial_constraints

def generate_lookup_table(db_name):
    """
    Generate a lookup table mapping each attribute to the set of DCs it is involved in.
    """
    denial_constraints = load_dc_config(db_name)
    lookup_table = {}

    for dc_label, attributes in denial_constraints.items():
        for attr in attributes:
            if attr not in lookup_table:
                lookup_table[attr] = set()
            lookup_table[attr].add(dc_label)

    return lookup_table

def print_lookup_table(lookup_table):
    for attr, dcs in lookup_table.items():
        print(f"Attribute: {attr}, Denial Constraints: {', '.join(dcs)}")

def main():
    parser = argparse.ArgumentParser(description='Generate denial constraint lookup table')
    parser.add_argument('--db', '--database', 
                      default='rtf25',
                      help='Database name (default: rtf25)')
    
    args = parser.parse_args()
    
    lookup = generate_lookup_table(args.db)
    print(f"Denial Constraint Lookup Table for '{args.db}':\n")
    print_lookup_table(lookup)

if __name__ == "__main__":
    main()

# lookup_table = generate_lookup_table()
# print_lookup_table(lookup_table)
# The output will show the attributes and the corresponding denial constraints associated with them.
# This lookup table can be used to quickly identify which denial constraints are relevant for a given attribute.
