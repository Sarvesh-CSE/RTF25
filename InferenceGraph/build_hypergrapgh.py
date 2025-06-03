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
            # Extract the column name after the dot, e.g. 'education' from 't1.education'
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


# 3) Build the “hyperedge_map” (each head → list of Hyperedges), unchanged:
def build_hyperedge_map(row: Dict[str, Any], key: Any, start_attr: str) -> Dict[Cell, List[Hyperedge]]:
    """
    Instead of merging all tails into one neighbor list, collect a mapping:
        head_cell → [ list of Hyperedges (each from one DC) ]

    We still do a BFS over attributes, but we store each Hyperedge separately.
    """
    # 3.1) Create a Cell object for every column in the row
    all_cells: Dict[str, Cell] = {}
    for col_name, val in row.items():
        attr = Attribute('adult_data', col_name)
        all_cells[col_name] = Cell(attr, key, val)

    # 3.2) Prepare a dict: head_cell → list of Hyperedges
    hyperedge_map: Dict[Cell, List[Hyperedge]] = {cell: [] for cell in all_cells.values()}

    # 3.3) BFS over attributes (just to discover new heads at each level)
    visited_attrs: Set[str] = {start_attr}
    frontier: List[str] = [start_attr]

    while frontier:
        next_frontier: List[str] = []
        for target_attr in frontier:
            head_cell = all_cells[target_attr]
            hyperedges = build_hyperedges(row, key, target_attr)

            for he in hyperedges:
                # 3.3.1) Record this entire Hyperedge under its head (separately)
                hyperedge_map[head_cell].append(he)

                # 3.3.2) Enqueue each tail‐attribute if not yet visited
                for tail_cell in he:
                    col = tail_cell.attribute.col
                    if col not in visited_attrs:
                        visited_attrs.add(col)
                        next_frontier.append(col)

        frontier = next_frontier

    return hyperedge_map


# ----------------------------------------------------------------------------- 
# 4) NEW: Recursively print a “tree” of hyperedges, rooted at `start_attr`:
def print_hyperedge_tree(
    row: Dict[str, Any],
    key: Any,
    start_attr: str,
    hyperedge_map: Dict[Cell, List[Hyperedge]],
    visited: Set[str] = None,
    indent: int = 0
):
    """
    Recursively print a tree of Hyperedges, rooted at `start_attr`, **skipping**
    any hyperedge whose tails have no previously-unseen attributes.
    """
    if visited is None:
        visited = {start_attr}

    # 1) Print the head cell
    head_cell = Cell(Attribute('adult_data', start_attr), key, row[start_attr])
    print("  " * indent + repr(head_cell))

    # 2) For each Hyperedge under this head, check if it has any NEW tail attribute
    for he in hyperedge_map.get(head_cell, []):
        # Find tails that are brand-new
        new_tails = [tail for tail in he if tail.attribute.col not in visited]
        if not new_tails:
            # All tails are already visited → skip this entire hyperedge
            continue

        # Otherwise, print the hyperedge (since it contributes at least one new attribute)
        print("  " * (indent + 1) + repr(he))

        # 3) Recurse only on those new tails
        for tail_cell in sorted(new_tails, key=lambda c: c.attribute.col):
            col = tail_cell.attribute.col
            visited.add(col)
            print_hyperedge_tree(row, key, col, hyperedge_map, visited, indent + 2)


# ----------------------------------------------------------------------------- 
# 5) Example usage: replace your old __main__ with this block
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
        if hes:  # only print heads that actually have hyperedges
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
