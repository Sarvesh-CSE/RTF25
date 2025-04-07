import pandas as pd

# This script will look into the DCs at the attribute level.
# For each attribute, a set of DCs are generated. Only these DCs are used for further graph generation for a given cell associated with some attribute.

def generate_lookup_table():
    denial_constraints = {
        "𝜙1": ["Tax", "Salary"],
        "𝜙2": ["Role", "SalPrHr"],
        "𝜙3": ["Salary", "SalPrHr", "WrkHr"],
        "𝜙4": ["Role", "SalPrHr"]
    }
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

lookup_table = generate_lookup_table()
print_lookup_table(lookup_table)
# The output will show the attributes and the corresponding denial constraints associated with them.
# This lookup table can be used to quickly identify which denial constraints are relevant for a given attribute.
