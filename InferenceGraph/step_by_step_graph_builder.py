# InferenceGraph/compact_tree_domains.py
"""
Compact script: Complete inference process for one target cell
1-4: Build hyperedges for target
5: Build tree 
6: Delete target cell
7: Compute domains from each DC
8: Intersect domains
"""

import sys# InferenceGraph/full_rtf_optimizer.py
"""
Full RTF Optimizer implementing the three-component architecture:
1. build_graph() - Dynamic incremental graph construction 
2. search() + check() - Greedy search with termination condition
3. IDcomputation() - Inferred domain computation after each deletion

Based on your compact_tree_domains.py foundation
"""

import sys
import os
from typing import Set, List, Dict, Tuple

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cell import Cell, Attribute
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints
from IDcomputation.IGC_c_get_global_domain_mysql import AttributeDomainComputation


class FullRTFOptimizer:
    """
    Complete RTF optimizer with three-component architecture
    """
    
    def __init__(self, threshold_alpha: float = 0.7):
        self.alpha = threshold_alpha
        self.domain_computer = AttributeDomainComputation('adult')
        print(f"RTF Optimizer initialized with threshold α = {threshold_alpha}")
    
    def find_minimal_deletion_set(self, target_key: int, target_attr: str) -> Set[Cell]:
        """
        Main optimization function implementing greedy iterative deletion
        """
        print(f"\n=== RTF Optimization ===")
        print(f"Target: {target_attr} in row {target_key}")
        
        # Initialize
        row = fetch_row(target_key)
        target_cell = Cell(Attribute('adult_data', target_attr), target_key, row[target_attr])
        deletion_set: Set[Cell] = set()
        iteration = 0
        
        print(f"Original cell value: {target_cell.value}")
        
        # === MAIN OPTIMIZATION LOOP ===
        while True:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # COMPONENT 2: CHECK - The brake function
            if self.check(target_cell, deletion_set, row):
                print("✓ Privacy threshold met - stopping")
                break
            
            # COMPONENT 1: BUILD_GRAPH - Dynamic incremental graph construction
            candidate_cells = self.build_graph(target_cell, deletion_set, row)
            
            if not candidate_cells:
                print("No more candidate cells available")
                break
            
            # COMPONENT 2: SEARCH - Greedy selection of best candidate
            best_candidate = self.search(target_cell, deletion_set, candidate_cells, row)
            
            if best_candidate is None:
                print("No beneficial candidate found")
                break
            
            # Add best candidate to deletion set
            deletion_set.add(best_candidate)
            print(f"Added to deletion set: {best_candidate.attribute.col}")
            
            # Safety limit
            if iteration > 15:
                print("Maximum iterations reached")
                break
        
        print(f"\n=== Optimization Complete ===")
        print(f"Final deletion set size: {len(deletion_set)}")
        return deletion_set
    
    def build_graph(self, target_cell: Cell, deletion_set: Set[Cell], row: Dict) -> List[Cell]:
        """
        COMPONENT 1: Dynamic incremental graph construction
        Expands the graph incrementally, adding new nodes as needed
        """
        print("Building incremental inference graph...")
        
        # Start with target cell's direct hyperedges
        hyperedge_map = build_hyperedge_map(row, target_cell.key, target_cell.attribute.col)
        
        # Collect all cells connected through hyperedges
        connected_cells = set()
        for head_cell, hyperedges in hyperedge_map.items():
            for hyperedge in hyperedges:
                for cell in hyperedge:
                    connected_cells.add(cell)
        
        # Expand to second-level connections (cells connected to already connected cells)
        second_level_cells = set()
        for cell in connected_cells:
            if cell != target_cell and cell not in deletion_set:
                try:
                    # Build hyperedges for this cell
                    cell_hyperedge_map = build_hyperedge_map(row, cell.key, cell.attribute.col)
                    for _, hyperedges in cell_hyperedge_map.items():
                        for hyperedge in hyperedges:
                            for c in hyperedge:
                                second_level_cells.add(c)
                except:
                    pass  # Skip if we can't build hyperedges for this cell
        
        # Combine all reachable cells
        all_reachable = connected_cells.union(second_level_cells)
        
        # Filter to get valid candidates
        candidates = []
        for cell in all_reachable:
            if (cell != target_cell and 
                cell not in deletion_set and
                row.get(cell.attribute.col) is not None):
                candidates.append(cell)
        
        print(f"  Found {len(candidates)} candidate cells")
        return candidates
    
    def search(self, target_cell: Cell, deletion_set: Set[Cell], candidates: List[Cell], row: Dict) -> Cell:
        """
        COMPONENT 2: Greedy search for best candidate
        Level-by-level, hyperedge-focused selection strategy
        """
        print(f"Evaluating {len(candidates)} candidates...")
        
        best_candidate = None
        best_improvement = 0
        
        # Current domain size (baseline)
        current_domain_size = self.IDcomputation(target_cell, deletion_set, row)
        
        for candidate in candidates:
            # Try adding this candidate
            trial_deletion_set = deletion_set.copy()
            trial_deletion_set.add(candidate)
            
            # COMPONENT 3: IDcomputation - Calculate effect
            trial_domain_size = self.IDcomputation(target_cell, trial_deletion_set, row)
            
            # Improvement = increase in domain size (more privacy)
            improvement = trial_domain_size - current_domain_size
            
            print(f"  {candidate.attribute.col}: domain {current_domain_size} → {trial_domain_size} (Δ={improvement})")
            
            if improvement > best_improvement:
                best_improvement = improvement
                best_candidate = candidate
        
        if best_candidate:
            print(f"Best candidate: {best_candidate.attribute.col} (improvement: +{best_improvement})")
        
        return best_candidate
    
    def check(self, target_cell: Cell, deletion_set: Set[Cell], row: Dict) -> bool:
        """
        COMPONENT 2: Check termination condition (the brake function)
        Returns True if privacy protection threshold is met
        """
        current_domain_size = self.IDcomputation(target_cell, deletion_set, row)
        
        # Get maximum possible domain size for this attribute
        max_domain_size = self.get_max_domain_size(target_cell.attribute.col)
        
        # Calculate privacy ratio
        privacy_ratio = current_domain_size / max_domain_size if max_domain_size > 0 else 0
        
        condition_met = privacy_ratio >= self.alpha
        
        print(f"Privacy check: domain_size={current_domain_size}/{max_domain_size} = {privacy_ratio:.3f} (threshold={self.alpha})")
        
        return condition_met
    
    def IDcomputation(self, target_cell: Cell, deletion_set: Set[Cell], row: Dict) -> int:
        """
        COMPONENT 3: Inferred domain computation (the constant calculator)
        Computes domain size after applying deletions - called after every deletion
        """
        target_attr = target_cell.attribute.col
        
        # Apply deletions
        modified_row = row.copy()
        for deleted_cell in deletion_set:
            if deleted_cell.attribute.col in modified_row:
                modified_row[deleted_cell.attribute.col] = None
        
        # If target cell itself is not deleted, domain size is 1
        if modified_row.get(target_attr) is not None:
            return 1
        
        # Target is deleted - compute inferred domain using your existing logic
        return self.compute_inferred_domain_size(target_cell, modified_row)
    
    def compute_inferred_domain_size(self, target_cell: Cell, modified_row: Dict) -> int:
        """
        Core domain computation using your existing compact logic
        """
        target_attr = target_cell.attribute.col
        
        # Build hyperedges for current state
        hyperedge_map = build_hyperedge_map(modified_row, target_cell.key, target_attr)
        target_hyperedges = hyperedge_map.get(target_cell, [])
        
        if not target_hyperedges:
            # No constraints - return full domain size
            return self.get_max_domain_size(target_attr)
        
        # Get possible values
        possible_values = self.get_possible_values(target_attr)
        
        # Compute domain from each hyperedge and intersect
        all_domains = []
        for hyperedge in target_hyperedges:
            domain = self.compute_domain_from_dc(target_cell, hyperedge, modified_row, possible_values)
            all_domains.append(domain)
        
        # Intersect all domains
        if all_domains:
            final_domain = set.intersection(*all_domains)
            return len(final_domain)
        else:
            return len(possible_values)
    
    def compute_domain_from_dc(self, target_cell: Cell, hyperedge, modified_row: Dict, possible_values: List) -> Set:
        """
        Compute valid values from one denial constraint (your existing logic)
        """
        target_attr = target_cell.attribute.col
        
        # Find corresponding denial constraint
        corresponding_dc = self.find_dc_for_hyperedge(hyperedge)
        if not corresponding_dc:
            return set(possible_values)
        
        # Test each value
        valid_values = set()
        for test_value in possible_values:
            test_row = modified_row.copy()
            test_row[target_attr] = test_value
            
            if not self.violates_dc(corresponding_dc, test_row):
                valid_values.add(test_value)
        
        return valid_values
    
    def get_possible_values(self, attr_name: str) -> List:
        """Get possible values using domain computation"""
        try:
            domain_info = self.domain_computer.get_domain('adult_data', attr_name)
            if domain_info:
                if domain_info['type'] == 'string':
                    return domain_info['values']
                elif domain_info['type'] == 'numeric':
                    min_val, max_val = domain_info['min'], domain_info['max']
                    if max_val - min_val <= 20:
                        return list(range(int(min_val), int(max_val) + 1))
                    else:
                        step = max(1, (max_val - min_val) // 20)
                        return list(range(int(min_val), int(max_val) + 1, step))
        except:
            pass
        
        # Fallback
        return ['Val1', 'Val2', 'Val3', 'Val4', 'Val5']
    
    def get_max_domain_size(self, attr_name: str) -> int:
        """Get maximum possible domain size for attribute"""
        possible_values = self.get_possible_values(attr_name)
        return len(possible_values)
    
    def find_dc_for_hyperedge(self, hyperedge) -> List:
        """Find denial constraint matching hyperedge (your existing logic)"""
        hyperedge_attrs = {cell.attribute.col for cell in hyperedge}
        
        for dc in denial_constraints:
            dc_attrs = set()
            for pred in dc:
                if len(pred) >= 3:
                    left_attr = pred[0].split('.')[-1] if '.' in pred[0] else pred[0]
                    right_attr = pred[2].split('.')[-1] if '.' in pred[2] else pred[2]
                    dc_attrs.add(left_attr)
                    dc_attrs.add(right_attr)
            
            if hyperedge_attrs.issubset(dc_attrs):
                return dc
        return None
    
    def violates_dc(self, dc: List, row: Dict) -> bool:
        """Check if row violates denial constraint (your existing logic)"""
        results = []
        
        for pred in dc:
            if len(pred) != 3:
                continue
            
            left_attr = pred[0].split('.')[-1] if '.' in pred[0] else pred[0]
            right_attr = pred[2].split('.')[-1] if '.' in pred[2] else pred[2]
            operator = pred[1]
            
            left_val = row.get(left_attr)
            right_val = row.get(right_attr)
            
            if left_val is None or right_val is None:
                results.append(False)
                continue
            
            try:
                if operator == '==':
                    results.append(left_val == right_val)
                elif operator == '!=':
                    results.append(left_val != right_val)
                elif operator == '>':
                    results.append(left_val > right_val)
                elif operator == '<':
                    results.append(left_val < right_val)
                else:
                    results.append(False)
            except:
                results.append(False)
        
        return all(results) if results else False


def main():
    """
    Demo the full RTF optimization process
    """
    print("Full RTF Optimizer Demo")
    print("=" * 30)
    
    # Test different threshold values
    thresholds = [0.3, 0.5, 0.7]
    
    for alpha in thresholds:
        print(f"\n{'='*50}")
        print(f"Testing with threshold α = {alpha}")
        
        optimizer = FullRTFOptimizer(threshold_alpha=alpha)
        
        deletion_set = optimizer.find_minimal_deletion_set(
            target_key=2, 
            target_attr='education'
        )
        
        print(f"\nResults for α = {alpha}:")
        print(f"Deletion set size: {len(deletion_set)}")
        for cell in deletion_set:
            print(f"  - Delete {cell.attribute.col} = {cell.value}")


def test_different_targets():
    """
    Test optimization for different target cells
    """
    print(f"\n{'='*50}")
    print("Testing Different Target Cells")
    
    test_cases = [
        (2, 'education'),
        (2, 'age'),
        (3, 'education'),
        (2, 'occupation')
    ]
    
    for target_key, target_attr in test_cases:
        print(f"\n--- Target: {target_attr} in row {target_key} ---")
        try:
            optimizer = FullRTFOptimizer(threshold_alpha=0.6)
            deletion_set = optimizer.find_minimal_deletion_set(target_key, target_attr)
            print(f"Result: {len(deletion_set)} deletions needed")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
    test_different_targets()
import os
from typing import Set, List

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cell import Cell, Attribute
from InferenceGraph.bulid_hyperedges import build_hyperedge_map, fetch_row
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints
from IDcomputation.IGC_c_get_global_domain_mysql import AttributeDomainComputation


def compute_inferred_domain(target_key: int, target_attr: str) -> Set:
    """
    Complete inference process in 8 steps
    """
    print(f"Computing inferred domain for {target_attr} in row {target_key}")
    
    # Steps 1-3: Get data and build hyperedges
    row = fetch_row(target_key)
    target_cell = Cell(Attribute('adult_data', target_attr), target_key, row[target_attr])
    hyperedge_map = build_hyperedge_map(row, target_key, target_attr)
    target_hyperedges = hyperedge_map.get(target_cell, [])
    
    print(f"  Found {len(target_hyperedges)} hyperedges")
    
    if not target_hyperedges:
        return set()
    
    # Step 6: Delete target cell
    modified_row = row.copy()
    modified_row[target_attr] = None
    print(f"  Deleted target cell")
    
    # Step 7: Compute domain from each hyperedge
    all_domains = []
    for i, hyperedge in enumerate(target_hyperedges):
        domain = compute_domain_from_dc(target_cell, hyperedge, modified_row)
        all_domains.append(domain)
        print(f"  Hyperedge {i+1}: {len(domain)} valid values")
    
    # Step 8: Intersect all domains
    final_domain = set.intersection(*all_domains) if all_domains else set()
    print(f"  Final domain: {len(final_domain)} values")
    
    return final_domain


def compute_domain_from_dc(target_cell: Cell, hyperedge, modified_row: dict) -> Set:
    """
    Compute valid values for target from one denial constraint
    """
    target_attr = target_cell.attribute.col
    
    # Get possible values using existing domain computation
    possible_values = get_possible_values(target_attr)
    
    # Find corresponding denial constraint
    corresponding_dc = find_dc_for_hyperedge(hyperedge)
    if not corresponding_dc:
        return set(possible_values)
    
    # Test each value
    valid_values = set()
    for test_value in possible_values:
        test_row = modified_row.copy()
        test_row[target_attr] = test_value
        
        if not violates_dc(corresponding_dc, test_row):
            valid_values.add(test_value)
    
    return valid_values


def get_possible_values(attr_name: str) -> List:
    """Get possible values using existing domain computation"""
    try:
        domain_computer = AttributeDomainComputation('adult')
        domain_info = domain_computer.get_domain('adult_data', attr_name)
        
        if domain_info:
            if domain_info['type'] == 'string':
                return domain_info['values']
            elif domain_info['type'] == 'numeric':
                min_val, max_val = domain_info['min'], domain_info['max']
                if max_val - min_val <= 20:
                    return list(range(int(min_val), int(max_val) + 1))
                else:
                    step = max(1, (max_val - min_val) // 20)
                    return list(range(int(min_val), int(max_val) + 1, step))
    except:
        pass
    
    # Fallback
    return ['Val1', 'Val2', 'Val3', 'Val4', 'Val5']


def find_dc_for_hyperedge(hyperedge) -> List:
    """Find denial constraint matching hyperedge attributes"""
    hyperedge_attrs = {cell.attribute.col for cell in hyperedge}
    
    for dc in denial_constraints:
        dc_attrs = set()
        for pred in dc:
            if len(pred) >= 3:
                left_attr = pred[0].split('.')[-1] if '.' in pred[0] else pred[0]
                right_attr = pred[2].split('.')[-1] if '.' in pred[2] else pred[2]
                dc_attrs.add(left_attr)
                dc_attrs.add(right_attr)
        
        if hyperedge_attrs.issubset(dc_attrs):
            return dc
    return None


def violates_dc(dc: List, row: dict) -> bool:
    """Check if row violates denial constraint"""
    results = []
    
    for pred in dc:
        if len(pred) != 3:
            continue
        
        left_attr = pred[0].split('.')[-1] if '.' in pred[0] else pred[0]
        right_attr = pred[2].split('.')[-1] if '.' in pred[2] else pred[2]
        operator = pred[1]
        
        left_val = row.get(left_attr)
        right_val = row.get(right_attr)
        
        if left_val is None or right_val is None:
            results.append(False)
            continue
        
        try:
            if operator == '==':
                results.append(left_val == right_val)
            elif operator == '!=':
                results.append(left_val != right_val)
            elif operator == '>':
                results.append(left_val > right_val)
            elif operator == '<':
                results.append(left_val < right_val)
            else:
                results.append(False)
        except:
            results.append(False)
    
    return all(results) if results else False


def main():
    """Test with one target cell"""
    print("Compact Inferred Domain Computation")
    print("=" * 40)
    
    # Test with education in row 2
    domain = compute_inferred_domain(target_key=2, target_attr='education')
    
    print(f"\nResult:")
    print(f"Inferred domain: {sorted(list(domain)) if domain else 'Empty'}")
    print(f"Domain size: {len(domain)}")


if __name__ == "__main__":
    main()