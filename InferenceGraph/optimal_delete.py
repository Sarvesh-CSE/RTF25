
from typing import Set
from collections import deque
import sys, os

# allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path for import resolution


from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row
from InferenceGraph.build_hypergraph import build_hypergraph_tree, GraphNode
from cell import Cell

def compute_costs(node: GraphNode) -> int:
    """
    Post‐order cost computation:
      cost = 1 + sum(min(child.cost) for each hyperedge)
    Also sets hyperedge.min_cell = the Cell with minimal cost.
    """
    total = 1
    for he, children in node.branches:
        # first compute costs for subtree
        for child in children:
            compute_costs(child)
        # pick the child with minimal cost
        # min_child = min(children, key=lambda c: c.cost)
        # Assume children is non-empty
        min_child = children[0]
        for c in children[1:]:
            if c.cost < min_child.cost:
                min_child = c

        he.min_cell = min_child.cell
        total += min_child.cost
    node.cost = total
    return total

def find_node(node: GraphNode, target: Cell) -> GraphNode:
    """
    DFS lookup of the GraphNode wrapping `target` Cell.
    """
    if node.cell == target:
        return node
    for _, children in node.branches:
        for child in children:
            found = find_node(child, target)
            if found:
                return found
    return None

def optimal_delete(root: GraphNode, deleted: Cell) -> Set[Cell]:
    """
    Implements the Java optimalDelete logic in Python:
      1) compute_costs over the entire tree
      2) BFS from the deleted cell’s node following hyperedge.min_cell pointers
    Returns the set of Cells to delete.
    """
    # 1) compute subtree costs and min_cell pointers
    compute_costs(root)

    # 2) locate the GraphNode for the deleted Cell
    start_node = find_node(root, deleted)
    if not start_node:
        return set()

    # 3) BFS following min_cell edges
    to_delete: Set[Cell] = {deleted}
    queue = deque([start_node])
    while queue:
        curr = queue.popleft()
        for he, _ in curr.branches:
            m = he.min_cell
            if m not in to_delete:
                to_delete.add(m)
                nxt = find_node(root, m) # we are doing O(n) tree traversals for each cell in the BFS queue!
                if nxt:
                    queue.append(nxt)

    return to_delete

def main():
    key = 2
    root_attr = 'education'

    # fetch the row and build the hyperedge map & tree
    row = fetch_row(key)
    hem = build_hyperedge_map(row, key, root_attr)
    root = build_hypergraph_tree(row, key, root_attr, hem)

    # run optimal-delete starting from the root cell
    to_remove = optimal_delete(root, root.cell)

    print("Cells to delete (optimal):")
    for c in to_remove:
        print(c)

if __name__ == '__main__':
    main()
