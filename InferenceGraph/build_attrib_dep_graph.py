import networkx as nx
import matplotlib.pyplot as plt
from collections import deque

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path for import resolution

# === STEP 1: Load denial constraints ===
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints 



# === STEP 2: Extract attributes from a DC ===

# dc = [
#     ("t1.education", "!=", "t2.education"),
#     ("t1.education_num", "==", "t2.education_num")
# ]

def extract_attributes(dc):
    attrs = set()
    for pred in dc:
        if len(pred) != 3: 
            print(f'the pred {pred} has an issue, take a look.')
            continue  # Skip malformed
        for side in (pred[0], pred[2]): # Check both left and right of the predicate
            if '.' in side: # e.g., "t1.education_num"
                attrs.add(side.split('.')[1])
    return attrs

def extract_all_head_tail_edges(target_attr, denial_constraints):
    """
    For a given target attribute and a list of target DCs,
    return a list of hyperedges {head, tail} where head == target_attr
    and tail contains all other attributes in that DC.
    """
    edges = []
    for dc in denial_constraints:
        involved = extract_attributes(dc)
        if target_attr in involved:
            tail = involved - {target_attr}
            if tail:
                edges.append({"head": target_attr, "tail": tail})
    print(f"Edges for {target_attr}: {edges}")
    return edges



# === STEP 3: Build dependency graph from DCs ===
def build_dependency_graph(target_attr, target_dc_list):
    graph = {} # Directed graph: attr → set of connected attrs
    visited = set()  # Keep track of already processed attributes
    queue = deque([target_attr]) # Start BFS from target_attr

    while queue:
        current_attr = queue.popleft()
        if current_attr in visited:
            continue
        visited.add(current_attr)

        for dc in target_dc_list:
            involved_attrs = extract_attributes(dc)
            if current_attr in involved_attrs:
                for attr in involved_attrs:
                    if attr != current_attr:
                        if current_attr not in graph:
                            graph[current_attr] =set()
                        graph[current_attr].add(attr)
                        queue.append(attr)
    print(graph)
    return graph

# === STEP 4: Visualization ===
def visualize_graph(graph, root):
    G = nx.DiGraph()
    for src, targets in graph.items():
        for tgt in targets:
            G.add_edge(src, tgt)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.title(f"Dependency Graph Rooted at '{root}'")
    plt.show()

# === STEP 5: Run for a specific target ===
if __name__ == "__main__":
    target_attr = "education_num"
    extract_all_head_tail_edges(target_attr, denial_constraints)
    # dependency_graph = build_dependency_graph(target_attr, target_dc_list)
    # print(f"Dependency graph for '{target_attr}':")
    # for k, v in dependency_graph.items():
    #     print(f"  {k} -> {sorted(v)}")

    # visualize_graph(dependency_graph, target_attr)
