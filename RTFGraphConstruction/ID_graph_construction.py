# incremental_graph_builder.py

import sys
import os
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cell import Attribute, Cell
from fetch_row import RTFDatabaseManager
from InferenceGraph.bulid_hyperedges import HyperedgeBuilder

class IncrementalGraphBuilder:
    def __init__(self, target_cell_info, dataset='adult'):
        self.target_cell_info = target_cell_info
        self.dataset = dataset
        self.hyperedge_builder = HyperedgeBuilder(dataset)
        self.hyperedge_graph = {}  # Store complete hyperedge structure
        self.nodes_in_graph = set()

    def _get_cell_id(self, cell):
        return (cell.attribute.table, cell.attribute.col, cell.key)

    def _fetch_row(self, key):
        with RTFDatabaseManager(self.dataset) as db:
            return db.fetch_row(key)

    def id_computation_stub(self, deletion_set):
        return False  # Always continue

    def check_threshold_stub(self):
        return False  # Always continue

    def construct_full_graph(self):
        # Initialize
        row_data = self._fetch_row(self.target_cell_info['key'])
        hyperedge_map = self.hyperedge_builder.build_hyperedge_map(
            row_data, self.target_cell_info['key'], self.target_cell_info['attribute'])
        
        # Create root
        root_cell = Cell(
            Attribute(self.hyperedge_builder.primary_table, self.target_cell_info['attribute']),
            self.target_cell_info['key'],
            row_data[self.target_cell_info['attribute']]
        )
        root_id = self._get_cell_id(root_cell)
        self.nodes_in_graph.add(root_id)
        self.hyperedge_graph[root_id] = []  # Store hyperedge branches
        
        # BFS expansion
        queue = deque([root_cell])
        while queue:
            current_cell = queue.popleft()
            current_id = self._get_cell_id(current_cell)
            
            for hyperedge in hyperedge_map.get(current_cell, []):
                if not self.check_threshold_stub():
                    self.id_computation_stub(set(self._get_cell_id(c) for c in hyperedge))
                    
                    # Store complete hyperedge structure
                    connected_cells = []
                    for cell in hyperedge:
                        cell_id = self._get_cell_id(cell)
                        connected_cells.append(cell_id)
                        
                        if cell_id not in self.nodes_in_graph:
                            self.nodes_in_graph.add(cell_id)
                            self.hyperedge_graph[cell_id] = []
                            queue.append(cell)
                    
                    # Store the complete hyperedge as a branch
                    self.hyperedge_graph[current_id].append((hyperedge, connected_cells))
        
        return self.hyperedge_graph

if __name__ == '__main__':
    target = {'key': 2, 'attribute': 'education'}
    builder = IncrementalGraphBuilder(target, 'adult')
    hyperedge_graph = builder.construct_full_graph()
    
    print(f"Graph: {len(builder.nodes_in_graph)} nodes")
    print(f"Hyperedge structure: {len(hyperedge_graph)} nodes with branches")
    
    # Show hyperedge structure
    for node_id, branches in hyperedge_graph.items():
        if branches:
            print(f"{node_id[1]} has {len(branches)} hyperedge branches")