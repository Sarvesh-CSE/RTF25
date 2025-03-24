import pandas as pd


# This script will lookinto the DCs at attribute level.
# For each attribute, a set of DCS are generated. Only these DCs are used for further graph generation.


def generate_lookup_table(denial_constraints):
    """
    Generates a lookup table for attributes involved in denial constraints.

    :param denial_constraints: A dictionary where keys are DC labels and values are lists of attributes.
    :return: A dictionary mapping each attribute to a set of relevant DCs.
    """
    lookup_table = {}

    # Iterate through each denial constraint
    for dc_label, attributes in denial_constraints.items():
        for attr in attributes:
            if attr not in lookup_table:
                lookup_table[attr] = set()  # Initialize set for unique DCs
            lookup_table[attr].add(dc_label)  # Add the DC label to the attribute

    return lookup_table


def print_lookup_table(lookup_table):
    """
    Prints the lookup table in a readable format.

    :param lookup_table: A dictionary mapping each attribute to a set of relevant DCs.
    """
    print("Lookup Table:")
    for attribute, dcs in lookup_table.items():
        print(f"{attribute}: {', '.join(dcs)}")


if __name__ == "__main__":
    # Given Denial Constraints (DCs) and their involved attributes
    denial_constraints = {
        "𝜙1": ["Tax", "Salary"],                # ¬(t1.Tax > t2.Tax ∧ t1.Salary < t2.Salary)
        "𝜙2": ["Role", "SalPrHr"],              # ¬(t1.Role > t2.Role ∧ t1.SalPrHr < t2.SalPrHr)
        "𝜙3": ["Salary", "SalPrHr", "WrkHr"],   # ¬(t1.Salary ≠ t1.SalPrHr × t1.WrkHr)
        "𝜙4": ["Role", "SalPrHr"]               # ¬(t1.Role = 1 ∧ t1.SalPrHr > 100)
    }

    # Generate the Lookup Table
    lookup_table = generate_lookup_table(denial_constraints)

    # Print the Lookup Table
    print_lookup_table(lookup_table)
