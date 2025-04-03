# dc_lookup.py
from dc_lookup import generate_lookup_table
from generate_data import fetch_database_state, filter_data, get_target_cell_location, delset

target_eid = 2
database_state = fetch_database_state(target_eid, delset)
filtered_data = filter_data(database_state, delset)
target_cell_location = get_target_cell_location(database_state, target_eid)

print("Filtered Data:", filtered_data)
print("Target Cell Location:", target_cell_location)

print("Accessing Lookup Table from another script:")

lookup_table = generate_lookup_table()

print(lookup_table)

