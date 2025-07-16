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
        
        # NEW: Track processed denial constraints to avoid cycles
        self.processed_constraints = set()
        self.constraint_to_hyperedges = {}  # Map DC index to hyperedges

    def _get_cell_id(self, cell):
        return (cell.attribute.table, cell.attribute.col, cell.key)

    def _fetch_row(self, key):
        with RTFDatabaseManager(self.dataset) as db:
            return db.fetch_row(key)

    def _get_constraint_signature(self, hyperedge, target_attr):
        """
        Create a unique signature for the denial constraint that generated this hyperedge.
        This prevents processing the same DC from different starting points.
        """
        # Get all attributes involved in this hyperedge
        attrs_in_hyperedge = {cell.attribute.col for cell in hyperedge}
        attrs_in_hyperedge.add(target_attr)  # Include the head attribute
        
        # Create a sorted, frozenset signature (order-independent)
        return frozenset(attrs_in_hyperedge)

    def _is_constraint_already_processed(self, hyperedge, target_attr):
        """
        Check if we've already processed the denial constraint that generated this hyperedge.
        """
        constraint_sig = self._get_constraint_signature(hyperedge, target_attr)
        return constraint_sig in self.processed_constraints

    def _mark_constraint_processed(self, hyperedge, target_attr):
        """
        Mark this denial constraint as processed to avoid future redundant exploration.
        """
        constraint_sig = self._get_constraint_signature(hyperedge, target_attr)
        self.processed_constraints.add(constraint_sig)

    def id_computation_stub(self, deletion_set):
        return False  # Always continue

    def check_threshold_stub(self):
        return False  # Always continue

    def construct_full_graph(self):
        print("=== Building Inference Graph (Avoiding DC Cycles) ===")
        
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
        self.hyperedge_graph[root_id] = []
        
        print(f"Root cell: {self.target_cell_info['attribute']} = {root_cell.value}")
        
        # BFS expansion with constraint tracking
        queue = deque([root_cell])
        iteration = 0
        
        while queue:
            iteration += 1
            current_cell = queue.popleft()
            current_id = self._get_cell_id(current_cell)
            current_attr = current_cell.attribute.col
            
            print(f"\n--- Iteration {iteration}: Processing {current_attr} ---")
            
            hyperedges_for_current = hyperedge_map.get(current_cell, [])
            print(f"Found {len(hyperedges_for_current)} potential hyperedges")
            
            processed_in_iteration = 0
            skipped_in_iteration = 0
            
            for hyperedge in hyperedges_for_current:
                # CHECK: Skip if this denial constraint was already processed
                if self._is_constraint_already_processed(hyperedge, current_attr):
                    skipped_in_iteration += 1
                    continue
                
                if not self.check_threshold_stub():
                    self.id_computation_stub(set(self._get_cell_id(c) for c in hyperedge))
                    
                    # Mark this constraint as processed BEFORE adding to queue
                    self._mark_constraint_processed(hyperedge, current_attr)
                    processed_in_iteration += 1
                    
                    # Store complete hyperedge structure
                    connected_cells = []
                    new_cells_added = 0
                    
                    for cell in hyperedge:
                        cell_id = self._get_cell_id(cell)
                        connected_cells.append(cell_id)
                        
                        if cell_id not in self.nodes_in_graph:
                            self.nodes_in_graph.add(cell_id)
                            self.hyperedge_graph[cell_id] = []
                            queue.append(cell)
                            new_cells_added += 1
                    
                    # Store the complete hyperedge as a branch
                    self.hyperedge_graph[current_id].append((hyperedge, connected_cells))
                    
                    # Log the constraint details
                    constraint_attrs = {cell.attribute.col for cell in hyperedge}
                    constraint_attrs.add(current_attr)
                    print(f"  ✓ Processed DC: {sorted(constraint_attrs)} → +{new_cells_added} new cells")
            
            print(f"  Summary: {processed_in_iteration} processed, {skipped_in_iteration} skipped (already covered)")
        
        print(f"\n=== Graph Construction Complete ===")
        print(f"Total nodes: {len(self.nodes_in_graph)}")
        print(f"Processed constraints: {len(self.processed_constraints)}")
        
        return self.hyperedge_graph

    def get_constraint_coverage_stats(self):
        """
        Analyze which denial constraints were processed and their coverage.
        """
        print("\n=== Constraint Coverage Analysis ===")
        
        for i, constraint_sig in enumerate(self.processed_constraints, 1):
            attrs = sorted(list(constraint_sig))
            print(f"DC-{i}: {' ↔ '.join(attrs)}")
        
        return {
            'total_constraints_processed': len(self.processed_constraints),
            'constraints': list(self.processed_constraints)
        }

if __name__ == '__main__':
    # Test the improved algorithm
    target = {'key': 2, 'attribute': 'education'}
    builder = IncrementalGraphBuilder(target, 'adult')
    hyperedge_graph = builder.construct_full_graph()
    
    # Show results
    print(f"\nFinal Graph: {len(builder.nodes_in_graph)} nodes")
    print(f"Hyperedge structure: {len(hyperedge_graph)} nodes with branches")
    
    # Show constraint coverage
    stats = builder.get_constraint_coverage_stats()
    
    # Show hyperedge structure (first 5 nodes)
    print(f"\n=== Sample Hyperedge Structure ===")
    for i, (node_id, branches) in enumerate(hyperedge_graph.items()):
        if i >= 5:  # Limit output
            break
        if branches:
            print(f"{node_id[1]} has {len(branches)} hyperedge branches")
            for j, (hyperedge, connected_cells) in enumerate(branches):
                connected_attrs = [cell_id[1] for cell_id in connected_cells]
                print(f"  Branch {j+1}: → {connected_attrs}")