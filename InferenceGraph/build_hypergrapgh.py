from typing import Any, List, Tuple, Dict, Set
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path for import resolution
import db_wrapper as dbw
from cell import Attribute, Cell, Hyperedge
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints

# ----------------------------------------------------------------------------- 
# 2) Build hyperedges for a single target attribute (unchanged)
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
            left_col = left.split('.')[1]
            right_col = right.split('.')[1]
            if left_col == target_attr or right_col == target_attr:
                head_idx = i
                break
        if head_idx is None:
            continue

        tail_preds = [pred for j, pred in enumerate(dc) if j != head_idx]
        cells: List[Cell] = []
        for (left, _, _) in tail_preds:
            col = left.split('.')[1]
            value = row[col]
            attr = Attribute('adult_data', col)
            cells.append(Cell(attr, key, value))

        he = Hyperedge(cells)
        keyset = frozenset(he)
        if keyset not in seen:
            seen[keyset] = he

    return list(seen.values())


# ----------------------------------------------------------------------------- 
# 3) Build the “hyperedge_map” (each head → list of Hyperedges), unchanged:
def build_hyperedge_map(row: Dict[str, Any], key: Any, start_attr: str) -> Dict[Cell, List[Hyperedge]]:
    """
    Instead of merging all tails into one neighbor list, collect a mapping:
        head_cell → [ list of Hyperedges (each from one DC) ]

    We still do a BFS over attributes, but we store each Hyperedge separately.
    """
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


# ----------------------------------------------------------------------------- 
# 4) Corrected: Recursively print a “tree” of hyperedges, rooted at `start_attr`,
# skipping any hyperedge whose tails are all already in the entry snapshot.
def print_hyperedge_tree(
    row: Dict[str, Any],
    key: Any,
    start_attr: str,
    hyperedge_map: Dict[Cell, List[Hyperedge]],
    visited: Set[str] = None,
    indent: int = 0
):
    """
    Print a true hyperedge‐tree rooted at `start_attr`, skipping any hyperedge whose
    tails are all already seen at the moment we stepped into this head. We take a 
    snapshot of visited attributes on entry, and compare each hyperedge’s tails 
    against that snapshot. As soon as we print a hyperedge, we mark *all* its tails 
    as visited so that no “stale” branch ever prints later.
    """
    if visited is None:
        visited = {start_attr}

    # 4.1) Print the head cell
    head_cell = Cell(Attribute('adult_data', start_attr), key, row[start_attr])
    print("  " * indent + repr(head_cell))

    # 4.2) Take a snapshot of visited attributes *before* handling any hyperedge
    entry_snapshot = set(visited)

    # 4.3) Iterate through each hyperedge under this head
    for he in hyperedge_map.get(head_cell, []):
        # 4.3a) If *all* tails of 'he' are in entry_snapshot, skip
        all_tails_visited = True
        for tail_cell in he:
            if tail_cell.attribute.col not in entry_snapshot:
                all_tails_visited = False
                break
        if all_tails_visited:
            continue

        # 4.3b) Otherwise, we print the hyperedge
        print("  " * (indent + 1) + repr(he))

        # 4.3c) Immediately mark *all* tail attributes as visited
        for tail_cell in he:
            visited.add(tail_cell.attribute.col)

        # 4.3d) Recurse on only those tails that were not in entry_snapshot
        new_tails = [tc for tc in he if tc.attribute.col not in entry_snapshot]
        for tail_cell in sorted(new_tails, key=lambda c: c.attribute.col):
            col = tail_cell.attribute.col
            print_hyperedge_tree(row, key, col, hyperedge_map, visited, indent + 2)


# ----------------------------------------------------------------------------- 
# 5) Example usage
if __name__ == '__main__':
    db = dbw.DatabaseWrapper(dbw.DatabaseConfig())
    key = 2
    sql = "SELECT * FROM adult_data WHERE id = %s LIMIT 1;"
    row = db.fetch_one(sql, (key,))
    print("Row:", row)

    root_attr = 'education'
    root_cell = Cell(Attribute('adult_data', root_attr), key, row[root_attr])

    # Build the hyperedge map (each head → list of Hyperedges)
    hyperedge_map = build_hyperedge_map(row, key, root_attr)

    # 5.1) Print each Hyperedge under its head, separately (flat view):
    print("\nHyperedges (one per DC) for each head:")
    for head_cell, hes in hyperedge_map.items():
        if hes:
            print(f"Head {head_cell}:")
            for he in hes:
                print("   ", he)

    # 5.2) Print only those under 'education' (flat):
    print("\nHyperedges under education[2]:")
    for he in hyperedge_map[root_cell]:
        print("   ", he)

    # 5.3) Print the full tree starting at 'education'
    print("\nHyperedge tree rooted at 'education':")
    print_hyperedge_tree(row, key, root_attr, hyperedge_map)

    db.close()
