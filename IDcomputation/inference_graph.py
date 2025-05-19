# Using the DC lookup table, this script generates the inference grapgh for target cell c.

import pandas as pd
import random
import networkx as nx
import csv
from RTF25.DataGeneration.proess_data import database_state
import sqlite3

def generate_lookup_table(denial_constraints):
    """
    Generates a lookup table for attributes involved in denial constraints.
    :param denial_constraints: A dictionary where keys are DC labels and values are lists of attributes.
    :return: A dictionary mapping each attribute to a set of relevant DCs.
    """
    lookup_table = {}
    for dc_label, attributes in denial_constraints.items():
        for attr in attributes:
            if attr not in lookup_table:
                lookup_table[attr] = set()
            lookup_table[attr].add(dc_label)
    return lookup_table

def construct_inference_graph(database_state, denial_constraints, delset, target_cell):
    """
    Constructs the inference graph Gc for a given target cell.
    :param database_state: The current database state.
    :param denial_constraints: Set of denial constraints.
    :param delset: Set of deletable cells.
    :param target_cell: The target cell for which inference protection is needed.
    :return: An inference graph as an adjacency list.
    """
    Gc = nx.DiGraph()
    lookup_table = generate_lookup_table(denial_constraints)
    
    for cell in delset:
        Gc.add_node(cell)
    
    for cell in delset:
        attr_cell = database_state.get(cell, None)
        if attr_cell and attr_cell in lookup_table:
            for constraint in lookup_table[attr_cell]:
                related_cells = [c for c in delset if database_state.get(c, None) in lookup_table[attr_cell]]
                for c1 in related_cells:
                    for c2 in related_cells:
                        if c1 != c2:
                            if not Gc.has_edge(c1, c2):
                                Gc.add_edge(c1, c2, constraints=set())
                            Gc[c1][c2]['constraints'].add(constraint)
    
    return Gc

if __name__ == "__main__":
    denial_constraints = {
        "𝜙1": ["Tax", "Salary"],
        "𝜙2": ["Role", "SalPrHr"],
        "𝜙3": ["Salary", "SalPrHr", "WrkHr"],
        "𝜙4": ["Role", "SalPrHr"]
    }
    

    # Read a random cell from tax.csv
    with open('tax.csv', mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header row to understand the schema
        # Check if the file has a column named "Salary"
        # Replace the "Salary" cell of a random row with NULL
        salary_index = header.index("Salary")
        rows = list(reader)
        if rows:
            random_row = random.choice(rows)
            random_row[salary_index] = "NULL"
            salary_index = header.index("Salary")
            cells = [row[salary_index] for row in reader]
        else:
            raise ValueError("The file does not contain a 'Salary' column.")
        target_cell = random.choice(cells)
    
    # Delete the selected cell from tax.csv
    with open('tax.csv', mode='r') as file:
        rows = list(csv.reader(file))
    
    with open('tax.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] != target_cell:  # Assuming the first column contains the cells
                writer.writerow(row)
    
    inference_graph = construct_inference_graph(database_state, denial_constraints, delset, target_cell)
    
    print("Inference Graph:")
    for edge in inference_graph.edges(data=True):
        print(edge)
