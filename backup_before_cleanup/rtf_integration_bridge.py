"""
Step 3: Integration Bridge
This connects your IncrementalGraphBuilder with IGC_e_get_bound_new
"""

import sys
sys.path.append('./RTFGraphConstruction')
sys.path.append('./IDcomputation')

from ID_graph_construction import IncrementalGraphBuilder
from IGC_e_get_bound_new import AttributeDomainComputation, DomianInferFromDC
from cell import Cell, Attribute

class RTFIntegrationBridge:
    """
    Bridge class that connects graph construction with ID computation
    This implements your multi-level analysis algorithm
    """
    
    def __init__(self, target_cell_info, dataset='adult', threshold_alpha=0.7):
        self.target_cell_info = target_cell_info
        self.dataset = dataset
        self.threshold = threshold_alpha
        
        # Initialize your existing components
        self.graph_builder = IncrementalGraphBuilder(target_cell_info, dataset)
        self.domain_computer = AttributeDomainComputation(dataset)
        self.domain_inferrer = DomianInferFromDC(dataset)
        
        # Algorithm state
        self.current_deletion_set = set()
        self.target_cell = None
        self.original_domain_size = 0
        self.current_domain_size = 0
        
        print(f"RTF Integration Bridge initialized")
        print(f"Target: {target_cell_info}")
        print(f"Threshold: {threshold_alpha}")
    
    def run_complete_algorithm(self):
        """
        Main method implementing your complete multi-level analysis algorithm
        """
        print(f"\n=== RTF Multi-Level Analysis Algorithm ===")
        
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
            if iteration > 50:
                print("Maximum iterations reached")
                break
        
        return self._generate_results()
    
    def _initialize_algorithm(self):
        """Initialize the algorithm with target cell and baseline domain"""
        print("--- Initialization ---")
        
        # Create target cell
        row_data = self._get_sample_row_data()  # You'll replace this
        self.target_cell = Cell(
            Attribute(self.dataset, self.target_cell_info['attribute']),
            self.target_cell_info['key'],
            row_data[self.target_cell_info['attribute']]
        )
        
        # Initialize deletion set with target cell
        self.current_deletion_set = {self.target_cell}
        
        # Calculate baseline domain sizes
        self.original_domain_size = self._get_original_domain_size()
        self.current_domain_size = self._compute_current_domain_size()
        
        print(f"Target cell: {self.target_cell.attribute.col} = {self.target_cell.value}")
        print(f"Original domain size: {self.original_domain_size}")
        print(f"Initial domain size: {self.current_domain_size}")
    
    def _inject_real_methods_into_graph_builder(self):
        """
        Replace the stub methods in IncrementalGraphBuilder with real implementations
        """
        print("--- Injecting real ID computation methods ---")
        
        # Replace id_computation_stub
        def real_id_computation(deletion_set):
            return self._compute_domains_for_deletion_set(deletion_set)
        
        # Replace check_threshold_stub  
        def real_threshold_check():
            return self._check_privacy_threshold()
        
        # Inject the real methods
        self.graph_builder.id_computation_stub = real_id_computation
        self.graph_builder.check_threshold_stub = real_threshold_check
        
        print("✓ Real methods injected into graph builder")
    
    def _find_candidate_cells(self):
        """
        Use graph construction to find candidate cells for deletion
        """
        print("Building inference graph to find candidates...")
        
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
                row_data = self._get_sample_row_data()  # You'll replace this
                if attr_name in row_data:
                    candidate = Cell(
                        Attribute(self.dataset, attr_name),
                        key,
                        row_data[attr_name]
                    )
                    candidate_cells.append(candidate)
        
        print(f"Found {len(candidate_cells)} candidate cells")
        return candidate_cells
    
    def _perform_multi_level_analysis(self, candidate_cells):
        """
        Implement Level 1 (Ordered Analysis) and Level 2 (Decision) phases
        """
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
        """
        Calculate benefit of deleting candidate cell (What-If analysis)
        """
        # Current domain size
        current_size = self.current_domain_size
        
        # Hypothetical deletion
        hypothetical_deletion_set = self.current_deletion_set.union({candidate_cell})
        hypothetical_size = self._compute_domain_size_for_deletion_set(hypothetical_deletion_set)
        
        # Benefit = increase in domain size
        benefit = hypothetical_size - current_size
        return benefit
    
    def _compute_current_domain_size(self):
        """Compute domain size for current deletion set"""
        return self._compute_domain_size_for_deletion_set(self.current_deletion_set)
    
    def _compute_domain_size_for_deletion_set(self, deletion_set):
        """
        Compute domain size using your existing ID computation logic
        """
        try:
            # Convert deletion set to format your ID computation expects
            deleted_attributes = [cell.attribute.col for cell in deletion_set]
            
            # Use your existing domain computation
            # This is where we integrate with your IGC_e_get_bound_new logic
            domain_size = self._use_existing_id_computation(deleted_attributes)
            
            return domain_size
            
        except Exception as e:
            print(f"Error in domain computation: {e}")
            # Fallback to original domain size
            return self.original_domain_size
    
    def _use_existing_id_computation(self, deleted_attributes):
        """
        Integration point with your existing IGC_e_get_bound_new logic
        """
        try:
            # Use your existing AttributeDomainComputation
            target_attr = self.target_cell.attribute.col
            
            # Get domain using your existing logic
            # You may need to adapt this based on your actual method signatures
            domain = self.domain_computer.get_domain(target_attr)
            
            if domain:
                # Apply constraints based on deletion set
                # This is simplified - you'll integrate your actual constraint logic
                remaining_domain_size = len(domain)
                
                # Reduce domain size based on deleted attributes (simplified)
                reduction_factor = len(deleted_attributes) * 0.1  # Mock reduction
                remaining_domain_size = max(1, int(remaining_domain_size * (1 + reduction_factor)))
                
                return remaining_domain_size
            
            return self.original_domain_size
            
        except Exception as e:
            print(f"Error using existing ID computation: {e}")
            return self.original_domain_size
    
    def _get_original_domain_size(self):
        """Get original domain size for target attribute"""
        try:
            domain = self.domain_computer.get_domain(self.target_cell.attribute.col)
            return len(domain) if domain else 5  # Fallback
        except:
            return 5  # Fallback
    
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
        # This gets called by your graph builder
        domain_size = self._compute_domain_size_for_deletion_set(deletion_set)
        return domain_size > 0  # Return boolean for stub compatibility
    
    def _get_sample_row_data(self):
        """
        REPLACE THIS with your actual data fetching logic
        """
        # Mock data - replace with your actual database/file access
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


# =====================================
# TEST THE INTEGRATION
# =====================================

def test_integration():
    """Test the integration bridge"""
    print("=== Testing RTF Integration Bridge ===")
    
    # Create bridge
    target_info = {'key': 2, 'attribute': 'education'}
    bridge = RTFIntegrationBridge(target_info, 'adult', 0.7)
    
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
    test_integration()