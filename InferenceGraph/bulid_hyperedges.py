from typing import Any, Dict, List, Set

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path for import resolution
from cell import Attribute, Cell, Hyperedge
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints
import db_wrapper as dbw

def fetch_row(key: int):
    db = dbw.DatabaseWrapper(dbw.DatabaseConfig())
    sql = "SELECT * FROM adult_data WHERE id = %s LIMIT 1;"
    row = db.fetch_one(sql, (key,))
    db.close()
    return row


# -----------------------------------------------------------------------------
# 1) Build hyperedges for a single target attribute

def build_hyperedges(row: Dict[str, Any], key: Any, target_attr: str) -> List[Hyperedge]:
    """
    For a given target_attr, extract one Hyperedge per DC where target_attr is the head.
    """
    seen: Dict[frozenset, Hyperedge] = {}
    for dc in denial_constraints:
        head_idx = None
        for i, (left, _, right) in enumerate(dc):
            left_col = left.split('.')[1]
            right_col = right.split('.')[1]
            if left_col == target_attr or right_col == target_attr:
                head_idx = i
                break
        if head_idx is None:
            continue
        # all other predicates become the tail
        tail_preds = [pred for j, pred in enumerate(dc) if j != head_idx]
        cells = []
        for (left, _, _) in tail_preds:
            col = left.split('.')[1]
            value = row[col]
            attr = Attribute('adult_data', col)
            cells.append(Cell(attr, key, value))

        he = Hyperedge(cells)
        keyset = frozenset(he)
        if keyset not in seen:
            seen[keyset] = he
    # print (seen.keys() )
    # print (seen.values()) # Convert to a list of Hyperedges
    return list(seen.values())

def build_hyperedge_map(row: Dict[str, Any], key: Any, start_attr: str) -> Dict[Cell, List[Hyperedge]]:
    all_cells: Dict[str, Cell] = {}
    for col_name, val in row.items():
        attr = Attribute('adult_data', col_name)
        all_cells[col_name] = Cell(attr, key, val)

    hyperedge_map: Dict[Cell, List[Hyperedge]] = {cell: [] for cell in all_cells.values()}

    visited_attrs: Set[str] = {start_attr}
    frontier: List[str] = [start_attr]

    while frontier:
        next_frontier: List[str] = []
        for target_attr in frontier:
            head_cell = all_cells[target_attr]
            hyperedges = build_hyperedges(row, key, target_attr)

            for he in hyperedges:
                hyperedge_map[head_cell].append(he)
                for tail_cell in he:
                    col = tail_cell.attribute.col
                    if col not in visited_attrs:
                        visited_attrs.add(col)
                        next_frontier.append(col)

        frontier = next_frontier

    return hyperedge_map



if __name__ == '__main__':
    key = 2
    row = fetch_row(key)

    root_attr = 'education'
    root_cell = Cell(Attribute('adult_data', root_attr), key, row[root_attr])
    hyperedges = build_hyperedges(row, key, root_attr)
    print(f"Hyperedges for {root_attr}:", hyperedges)

    hyperedge_map = build_hyperedge_map(row, key, root_attr)

    # Flat view
    print("\nFlat hyperedges for each head:")
    for head, hes in hyperedge_map.items():
        if hes:
            print(f"Head {head}:")
            for he in hes:
                print("  ", he)
