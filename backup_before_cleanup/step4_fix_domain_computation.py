"""
Step 4: Fix Domain Computation Integration
This fixes the issues found in Step 3 testing
"""

import sys
sys.path.append('./RTFGraphConstruction')
sys.path.append('./IDcomputation')

from ID_graph_construction import IncrementalGraphBuilder
from IGC_e_get_bound_new import AttributeDomainComputation, DomianInferFromDC
from cell import Cell, Attribute

class RTFIntegrationBridgeFixed:
    """
    Fixed version of the integration bridge with proper domain computation
    """
    
    def __init__(self, target_cell_info, dataset='adult', threshold_alpha=0.3):
        self.target_cell_info = target_cell_info
        self.dataset = dataset
        self.threshold = threshold_alpha  # Lower threshold for testing
        
        # Initialize your existing components
        self.graph_builder = IncrementalGraphBuilder(target_cell_info, dataset)
        self.domain_computer = AttributeDomainComputation(dataset)
        self.domain_inferrer = DomianInferFromDC(dataset)
        
        # Algorithm state
        self.current_deletion_set = set()
        self.target_cell = None
        self.original_domain_size = 0
        self.current_domain_size = 0
        
        print(f"RTF Integration Bridge (Fixed) initialized")
        print(f"Target: {target_cell_info}")
        print(f"Threshold: {threshold_alpha}")
    
    def run_complete_algorithm(self):
        """
        Main method implementing your complete multi-level analysis algorithm
        """
        print(f"\n=== RTF Multi-Level Analysis Algorithm (Fixed) ===")
        
        # === INITIALIZATION ===
        self._initialize_algorithm()
        
        # === MAIN ALGORITHM LOOP ===
        iteration = 0
        
        # Replace the stub methods in graph_builder
        self._inject_real_methods_into_graph_builder()
        
        while True:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # CHECK: Privacy threshold met?
            if self._check_privacy_threshold():
                print("✓ Privacy threshold achieved - stopping")
                break
            
            # LEVEL 1: Find candidate cells using graph construction
            candidate_cells = self._find_candidate_cells()
            
            if not candidate_cells:
                print("No more candidate cells found")
                break
            
            # LEVEL 2: Multi-level analysis to select best candidate
            best_candidate = self._perform_multi_level_analysis(candidate_cells)
            
            if not best_candidate:
                print("No beneficial candidate found")
                break
            
            # LEVEL 3: Execute deletion
            print(f"Selected for deletion: {best_candidate.attribute.col}")
            self.current_deletion_set.add(best_candidate)
            
            # Update domain size
            self.current_domain_size = self._compute_current_domain_size()
            print(f"New domain size: {self.current_domain_size}")
            
            # Safety break
            if iteration > 10:
                print("Maximum iterations reached")
                break
        
        return self._generate_results()
    
    def _initialize_algorithm(self):
        """Initialize the algorithm with target cell and baseline domain"""
        print("--- Initialization ---")
        
        # Create target cell
        row_data = self._get_sample_row_data()
        self.target_cell = Cell(
            Attribute(self.dataset, self.target_cell_info['attribute']),
            self.target_cell_info['key'],
            row_data[self.target_cell_info['attribute']]
        )
        
        # Initialize deletion set with target cell
        self.current_deletion_set = {self.target_cell}
        
        # Calculate baseline domain sizes - FIXED METHOD CALL
        self.original_domain_size = self._get_original_domain_size_fixed()
        self.current_domain_size = self._compute_current_domain_size()
        
        print(f"Target cell: {self.target_cell.attribute.col} = {self.target_cell.value}")
        print(f"Original domain size: {self.original_domain_size}")
        print(f"Initial domain size: {self.current_domain_size}")
    
    def _get_original_domain_size_fixed(self):
        """Get original domain size for target attribute - FIXED VERSION"""
        try:
            # FIX: Call get_domain with correct parameter name
            domain = self.domain_computer.get_domain(column=self.target_cell.attribute.col)
            domain_size = len(domain) if domain else 10
            print(f"Domain for {self.target_cell.attribute.col}: {domain_size} values")
            return domain_size
        except Exception as e:
            print(f"Error getting original domain: {e}")
            return 10  # Fallback
    
    def _inject_real_methods_into_graph_builder(self):
        """Replace the stub methods with real implementations"""
        print("--- Injecting real ID computation methods ---")
        
        def real_id_computation(deletion_set):
            return self._compute_domains_for_deletion_set(deletion_set)
        
        def real_threshold_check():
            return self._check_privacy_threshold()
        
        self.graph_builder.id_computation_stub = real_id_computation
        self.graph_builder.check_threshold_stub = real_threshold_check
        
        print("✓ Real methods injected into graph builder")
    
    def _find_candidate_cells(self):
        """Use graph construction to find candidate cells for deletion"""
        print("Building inference graph to find candidates...")
        
        try:
            # Use your existing graph construction
            hyperedge_graph = self.graph_builder.construct_full_graph()
            
            # Extract candidate cells from the graph
            candidate_cells = []
            
            for node_id, branches in hyperedge_graph.items():
                attr_name, key = node_id
                
                # Skip if already in deletion set
                cell_already_deleted = any(
                    cell.attribute.col == attr_name and cell.key == key 
                    for cell in self.current_deletion_set
                )
                
                if not cell_already_deleted and branches:
                    # Create candidate cell
                    row_data = self._get_sample_row_data()
                    if attr_name in row_data:
                        candidate = Cell(
                            Attribute(self.dataset, attr_name),
                            key,
                            row_data[attr_name]
                        )
                        candidate_cells.append(candidate)
            
            print(f"Found {len(candidate_cells)} candidate cells")
            return candidate_cells
            
        except Exception as e:
            print(f"Error in graph construction: {e}")
            # Return some mock candidates for testing
            return self._get_mock_candidates()
    
    def _get_mock_candidates(self):
        """Generate mock candidates for testing when graph construction fails"""
        print("Using mock candidates for testing...")
        row_data = self._get_sample_row_data()
        
        candidates = []
        # Create candidates from related attributes
        related_attrs = ['age', 'workclass', 'occupation', 'marital-status']
        
        for attr in related_attrs:
            if attr in row_data:
                candidate = Cell(
                    Attribute(self.dataset, attr),
                    self.target_cell_info['key'],
                    row_data[attr]
                )
                candidates.append(candidate)
        
        return candidates
    
    def _perform_multi_level_analysis(self, candidate_cells):
        """Implement Level 1 and Level 2 phases"""
        print("--- Level 1: Ordered Analysis Phase ---")
        
        potential_plans = []
        
        for i, candidate in enumerate(candidate_cells):
            print(f"Analyzing candidate {i+1}: {candidate.attribute.col}")
            
            # Calculate benefit of deleting this candidate
            benefit = self._calculate_deletion_benefit(candidate)
            
            if benefit > 0:
                potential_plans.append((benefit, candidate))
                print(f"  Benefit: {benefit}")
            else:
                print(f"  No benefit: {benefit}")
        
        print("--- Level 2: Decision Phase ---")
        
        if not potential_plans:
            return None
        
        # Sort by benefit (highest first)
        potential_plans.sort(key=lambda x: x[0], reverse=True)
        best_benefit, best_candidate = potential_plans[0]
        
        print(f"Selected candidate with benefit: {best_benefit}")
        return best_candidate
    
    def _calculate_deletion_benefit(self, candidate_cell):
        """Calculate benefit of deleting candidate cell (What-If analysis)"""
        current_size = self.current_domain_size
        
        # Hypothetical deletion
        hypothetical_deletion_set = self.current_deletion_set.union({candidate_cell})
        hypothetical_size = self._compute_domain_size_for_deletion_set(hypothetical_deletion_set)
        
        benefit = hypothetical_size - current_size
        return benefit
    
    def _compute_current_domain_size(self):
        """Compute domain size for current deletion set"""
        return self._compute_domain_size_for_deletion_set(self.current_deletion_set)
    
    def _compute_domain_size_for_deletion_set(self, deletion_set):
        """FIXED: Compute domain size using proper constraint-based reduction"""
        try:
            # Convert deletion set to attribute names
            deleted_attributes = set(cell.attribute.col for cell in deletion_set)
            target_attr = self.target_cell.attribute.col
            
            # Start with original domain
            original_domain = self.domain_computer.get_domain(column=target_attr)
            if not original_domain:
                return self.original_domain_size
            
            # IMPROVED: Apply constraint-based domain reduction
            remaining_domain_size = len(original_domain)
            
            # For each deleted attribute, reduce the domain
            # This is a simplified model - you'll replace with your actual constraint logic
            for deleted_attr in deleted_attributes:
                if deleted_attr != target_attr:
                    # Simulate constraint effect: each deleted related attribute increases domain
                    # by reducing constraint power
                    increase_factor = self._get_constraint_strength(target_attr, deleted_attr)
                    remaining_domain_size = min(
                        self.original_domain_size,
                        int(remaining_domain_size * (1 + increase_factor))
                    )
            
            return remaining_domain_size
            
        except Exception as e:
            print(f"Error in domain computation: {e}")
            return self.original_domain_size
    
    def _get_constraint_strength(self, target_attr, deleted_attr):
        """Estimate constraint strength between attributes"""
        # Mock constraint strengths - replace with your actual constraint analysis
        constraint_map = {
            ('education', 'age'): 0.2,
            ('education', 'workclass'): 0.3,
            ('education', 'occupation'): 0.4,
            ('education', 'marital-status'): 0.1,
        }
        
        key = (target_attr, deleted_attr)
        return constraint_map.get(key, 0.1)  # Default weak constraint
    
    def _check_privacy_threshold(self):
        """Check if privacy threshold is met"""
        if self.original_domain_size == 0:
            return True
        
        privacy_ratio = self.current_domain_size / self.original_domain_size
        met = privacy_ratio >= self.threshold
        
        print(f"Privacy check: {self.current_domain_size}/{self.original_domain_size} = {privacy_ratio:.3f} (threshold: {self.threshold}) -> {'✓' if met else '✗'}")
        
        return met
    
    def _compute_domains_for_deletion_set(self, deletion_set):
        """Method to replace id_computation_stub"""
        domain_size = self._compute_domain_size_for_deletion_set(deletion_set)
        return domain_size > 0
    
    def _get_sample_row_data(self):
        """Mock data - you'll replace this with your actual data access"""
        return {
            'age': 39,
            'workclass': 'State-gov', 
            'education': 'Bachelors',
            'marital-status': 'Never-married',
            'occupation': 'Adm-clerical',
            'relationship': 'Not-in-family',
            'race': 'White',
            'sex': 'Male',
            'hours-per-week': 40,
            'native-country': 'United-States',
            'income': '<=50K'
        }
    
    def _generate_results(self):
        """Generate final results"""
        results = {
            'deletion_set': self.current_deletion_set,
            'final_domain_size': self.current_domain_size,
            'original_domain_size': self.original_domain_size,
            'privacy_ratio': self.current_domain_size / self.original_domain_size if self.original_domain_size > 0 else 1.0,
            'threshold_met': self._check_privacy_threshold()
        }
        
        return results


def test_fixed_integration():
    """Test the fixed integration"""
    print("=== Testing FIXED RTF Integration Bridge ===")
    
    # Create bridge with lower threshold so it doesn't stop immediately
    target_info = {'key': 2, 'attribute': 'education'}
    bridge = RTFIntegrationBridgeFixed(target_info, 'adult', 0.3)  # Lower threshold
    
    # Run algorithm
    results = bridge.run_complete_algorithm()
    
    # Display results
    print(f"\n=== RESULTS ===")
    print(f"Deletion set size: {len(results['deletion_set'])}")
    print(f"Final domain size: {results['final_domain_size']}")
    print(f"Original domain size: {results['original_domain_size']}")
    print(f"Privacy ratio: {results['privacy_ratio']:.3f}")
    print(f"Threshold met: {results['threshold_met']}")
    
    print("\nCells to delete:")
    for cell in results['deletion_set']:
        print(f"  - {cell.attribute.col}: {cell.value}")

if __name__ == '__main__':
    test_fixed_integration()