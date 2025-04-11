
from proess_data import fetch_database_state, filter_data, get_target_cell_location, delset, target_eid

from typing import List, Tuple, Union, Set

Interval = Tuple[int, int]  # A numerical range
Domain = Union[List[Interval], Set[str]]  # Could be range (for numeric) or set (for categorical)
Cell = Tuple[int, str] # a Cell should be a tuple of one integer and one string (like eid= 2, attr= "salary")

print(delset)
print("Target EID:", target_eid)
delset_actual = set()
for cell in delset:
    delset_actual.add((target_eid, cell))
print("Delset Actual:", delset_actual)

def get_global_domain(Dt: dict, attr: str, delset: Set[Cell]) -> Domain:
    values = set()
    for t in Dt:
        cell = (t, attr)
        if cell not in delset or Dt[t].get(attr) is not None:
            values.add(Dt[t][attr])

    if values:
        if all(isinstance(v, (int, float)) for v in values):
            return [(min(values), max(values))]
        else:
            return values
    else:
        return [(-float('inf'), float('inf'))] if attr == 'numeric' else {"ALL"}
    
if __name__ == "__main__":
    # GetGlobalDomain example
    Dt = {
        1: {"age": 25, "color": "red"},
        2: {"age": 30, "color": "blue"},
        3: {"age": None, "color": "green"}
    }
    delset = {(3, "age")}
    print("Global Domain (numeric):", get_global_domain(Dt, "age", delset))  # [(25, 30)]
    print("Global Domain (categorical):", get_global_domain(Dt, "color", set()))  # {'red', 'blue', 'green'}

 
