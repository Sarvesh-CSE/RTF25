# InferenceGraph

This subfolder builds dependency graphs, instantiates hyperedges from DCs, and computes minimal deletion sets.

## Scripts

* **bulid\_hyperedges.py**
  For a given target row and attribute:

  1. **Fetches** the database row via `fetch_row`.
  2. Scans all DCs to **build hyperedges** mapping head predicates → tail cells.
  3. Returns a mapping of hyperedges used by `build_hypergraph.py`.
  

* **build\_hypergraph.py**
  Traverses the attribute graph to instantiate the **cell‑level hypergraph** Δ(c):

  * Creates `GraphNode` objects for each reachable *Cell*.
  * Records `node.branches` for each hyperedge instantiation.

* **optimal\_delete.py**
  Implements `optimal_delete(root, deleted)` using:

  1. **`compute_costs`** – a post‑order DFS to label each `GraphNode.cost = 1 + sum(min child cost)` and mark each `he.min_cell`.
  2. **`find_node`** – DFS to locate the `GraphNode` for any `Cell`.
  3. **BFS** – starting from the deleted cell’s node, follow each `he.min_cell` pointer to collect the minimal deletion set.

