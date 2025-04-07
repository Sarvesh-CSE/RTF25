# Importing necessary custom modules
from dc_lookup import generate_lookup_table
from proess_data import fetch_database_state, filter_data, get_target_cell_location, delset

# Current script specific imports
from collections import defaultdict


# Given inputs
target_eid = 2
print(delset)
database_state = fetch_database_state(target_eid, delset)
filtered_data = filter_data(database_state, delset)
target_cell_location = get_target_cell_location(database_state, target_eid)

print("Filtered Data:", filtered_data)
print("Target Cell Location:", target_cell_location)

print("Accessing Lookup Table from another script:")

lookup_table = generate_lookup_table()

print(lookup_table)

delset_c = [
    {"table": "Tax", "column": "Salary", "row": 2}
]

target_cell = {"table": "Tax", "column": "Salary", "row": 2}


def index_constraints(Phi):
    """
    Index constraints by attributes they involve.
    """
    L = defaultdict(set)
    for phi, attrs in Phi.items():
        for attr in attrs:
            L[attr].add(phi)
    print ("Indexed Constraints:", L)
    return L
Phi = {
    "𝜙1": ["Tax", "Salary"],
    "𝜙2": ["Role", "SalPrHr"],
    "𝜙3": ["Salary", "SalPrHr", "WrkHr"],
    "𝜙4": ["Role", "SalPrHr"]
}
index_constraints(Phi)



def construct_inference_graph(database_state, Phi, delset_c, target_cell):
    """
    Constructs the inference graph Gc.
    
    :param Dt: Database state
    :param Phi: Set of denial constraints (DCs)
    :param delset_c: Set of deletable cells
    :param target_cell: Target cell location
    :return: Adjacency list representation of inference graph Gc
    """
    Gc = defaultdict(set)  # Adjacency list for the inference graph
    
    # Step 3: Get indexed constraints
    L = index_constraints(Phi)
    
    # Step 4-5: Add deletable cells as nodes in Gc
    for ci in delset:
        Gc[ci] = set()
    print("Initial Inference Graph Gc:", Gc)
    
    # Step 6-11: Establish connections based on constraints
    for ci in delset:
        attr_ci = get_attribute(ci, database_state)
        
        if attr_ci in L:
            for phi in L[attr_ci]:
                cells_phi = {c for c in instantiate(phi, database_state) if c in delset_c}
                
                for cj in cells_phi:
                    for ck in cells_phi:
                        if cj != ck:
                            Gc[cj].add(ck)
                            Gc[ck].add(cj)
    print("Inference Graph Gc:", Gc)
    return Gc



def get_attribute(cell, Dt):
    """
    Retrieves the attribute name for a given cell in Dt.
    """
    table, column, row = cell['table'], cell['column'], cell['row']
    return column

def instantiate(phi, Dt):
    """
    Retrieve the set of instantiated cells related to a denial constraint phi in Dt.
    """
    related_attrs = Phi[phi]
    cells = set()
    for table, data in Dt.items():
        for row_idx, row in enumerate(data):
            for col in related_attrs:
                if col in row:
                    cells.add({'table': table, 'column': col, 'row': row_idx})
    return cells


# Construct the inference graph
Gc = construct_inference_graph(database_state={}, Phi=Phi, delset_c=delset_c, target_cell=target_cell)

# Print the inference graph
print(dict(Gc))


