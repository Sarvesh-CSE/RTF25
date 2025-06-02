from typing import Any, List, Tuple, Dict
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path for import resolution
import db_wrapper as dbw
from cell import Attribute, Cell, Hyperedge
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints
# This script builds a hypergraph from denial constraints (DCs) and a database table.


# 1) Denial constraints (DCs)
#    Each DC is a list of predicates of the form (left_attr, operator, right_attr)
#    where left_attr/right_attr are strings like 't1.education' or 't2.education_num'.


# 2) Build hyperedges for a single target attribute
def build_hyperedges(row: Dict[str, Any], key: Any, target_attr: str) -> List[Hyperedge]:
    """
    Given one fetched row (mapping column→value) and the primary key,
    find all DCs where any predicate mentions `target_attr`.
    For each such DC, treat the matching predicate as head, bundle all other
    predicates into one Hyperedge, and return the deduplicated list of edges.
    """
    seen: Dict[frozenset, Hyperedge] = {}

    for dc in denial_constraints:
        head_idx = None
        for i, (left, _, right) in enumerate(dc):
            # Extract just the column name after the dot, e.g. 'education' from 't1.education'
            left_col = left.split('.')[1]
            right_col = right.split('.')[1]
            if left_col == target_attr or right_col == target_attr:
                head_idx = i
                break
        if head_idx is None:
            continue

        # All other predicates in this DC become the tail:
        tail_preds = [pred for j, pred in enumerate(dc) if j != head_idx]

        # Build a Hyperedge by wrapping each tail predicate's column into a Cell:
        cells: List[Cell] = []
        for (left, _, _) in tail_preds:
            col = left.split('.')[1]              # e.g. 'education_num'
            value = row[col]                       # fetch value from the row
            attr = Attribute('adult_data', col)    # same table "adult_data"
            cells.append(Cell(attr, key, value))

        he = Hyperedge(cells)
        keyset = frozenset(he)  # use frozen set of Cell for deduplication
        if keyset not in seen:
            seen[keyset] = he

    return list(seen.values())

# 3) Build the full DC‐driven graph for one tuple
def build_graph(row: Dict[str, Any], key: Any) -> Dict[Cell, List[Cell]]:
    """
    Constructs an adjacency‐list representation of the DC‐driven graph 
    over all cells in `row`. Each Cell is a node. For any two cells that 
    co‐occur in the same Hyperedge, we add an undirected edge between them.
    """
    # 3.1 Create a Cell object for every column in the row
    all_cells: Dict[str, Cell] = {}
    for col_name, val in row.items():
        attr = Attribute('adult_data', col_name)
        all_cells[col_name] = Cell(attr, key, val)
    # print("All cells:", all_cells)

    # 3.2 Initialize adjacency map: each Cell → empty list of neighbors
    adjacency: Dict[Cell, List[Cell]] = {cell_obj: [] for cell_obj in all_cells.values()}

    # 3.3 For each column name, generate hyperedges and link cells pairwise
    for target_attr in row.keys():
        hyperedges = build_hyperedges(row, key, target_attr)
        for he in hyperedges:
            he_cells = list(he)
            for i in range(len(he_cells)):
                for j in range(i+1, len(he_cells)):
                    u, v = he_cells[i], he_cells[j]
                    adjacency[u].append(v)
                    adjacency[v].append(u)

    return adjacency

# 4) Example usage
if __name__ == '__main__':
    db = dbw.DatabaseWrapper(dbw.DatabaseConfig())
    key = 2
    sql = "SELECT * FROM adult_data WHERE id = %s LIMIT 1;"
    row = db.fetch_one(sql, (key,))
    print("Row:", row)

    # 4.1 Print hyperedges for 'education'
    education_edges = build_hyperedges(row, key, 'education')
    print("\nHyperedges for 'education':")
    for e in education_edges:
        print("  ", e)

    # 4.2 Build and display the full DC-violation graph
    graph = build_graph(row, key)
    print("\nGraph adjacency list:")
    for head_cell, neighbors in graph.items():
        print(f"  {head_cell} → {neighbors}")

    db.close()
