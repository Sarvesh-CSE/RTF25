# # Importing necessary custom modules
# import sys
# sys.path.append('../DataGeneration')
from dc_lookup import generate_lookup_table
from proess_data import fetch_database_state, filter_data, get_target_cell_location, delset, target_eid


print(delset)
database_state = fetch_database_state(target_eid, delset)
filtered_data = filter_data(database_state, delset)
target_cell_location = get_target_cell_location(database_state, target_eid)

print("Database State:", database_state)
print("Filtered Data:", filtered_data)
print("Target Cell Location:", target_cell_location)

print("Accessing Lookup Table from another script:")

lookup_table = generate_lookup_table()

print(lookup_table)


def index_constraints(Phi):
    """
    Index constraints by attributes they involve.
    """
    L = {}
    for phi, attrs in Phi.items():
        for attr in attrs:
            if attr not in L:
                L[attr] = set()
            L[attr].add(phi)
    # print ("Indexed Constraints:", L)
    return L
Phi = {
    "𝜙1": ["Tax", "Salary"],
    "𝜙2": ["Role", "SalPrHr"],
    "𝜙3": ["Salary", "SalPrHr", "WrkHr"],
    "𝜙4": ["Role", "SalPrHr"]
}
L=index_constraints(Phi)
print("The phi: ", L)



def construct_inference_graph(Phi, delset):
    Gc = {}  # Adjacency list for the inference graph
    
    # Step 3: Get indexed constraints
    L = index_constraints(Phi)
    
    # Step 4-5: Add deletable cells as nodes in Gc (and 6-7 combined)
    for ci in delset:
        Gc[ci] = set()
    print("Initial Inference Graph Gc:", Gc)

    for ci in delset: # step 6
        # Step 8: For each cell in delset, find the constraints it belongs to
        if ci in L:
            for phi in L[ci]:
                # Step 9: For each constraint, find the cells involved in it
                for cell in Phi[phi]:
                    if cell != ci and cell in delset:
                        Gc[ci].add(cell)
    


# This is a workig code for the inference graph construction with respect to the target cell location. 
# This is more optimized way of doing graph construction.
    # target_column = target_cell_location['column']
    # if target_column in L:
    #     cells_phi = []
    #     for phi in L[target_column]:
    #         # Identify cells in delset that are part of the current constraint attributes
    #         for cell in Phi[phi]:
    #             if cell in delset:
    #                 if cell not in cells_phi:
    #                     cells_phi.append(cell)

    #     for ci in cells_phi:
    #         if ci != target_column:
    #             Gc[ci].add(target_column)
    #             print("Adding edge:", ci, target_column)


    # print("Inference Graph Gc:", Gc)
    return Gc




# Construct the inference graph
Gc = construct_inference_graph(Phi=Phi, delset=delset)

# Print the inference graph
print(dict(Gc))


