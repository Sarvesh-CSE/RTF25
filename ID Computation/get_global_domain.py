
from typing import List, Tuple, Union, Set

Interval = Tuple[int, int]  # A numerical range
Domain = Union[List[Interval], Set[str]]  # Could be range (for numeric) or set (for categorical)

def get_global_domain(Dt: dict, attr: str, delset: Set[Tuple[int, str]]) -> Domain:
    values = set()
    for t in Dt:
        cell = (t, attr)
        if cell not in delset and Dt[t].get(attr) is not None:
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

 
