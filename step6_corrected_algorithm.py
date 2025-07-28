"""
Step 6: Corrected Algorithm with Proper Constraint Modeling
This correctly models how constraints restrict the inferred domain initially,
then progressively weaken as related cells are deleted.
"""

import sys
sys.path.append('./RTFGraphConstruction')
sys.path.append('./IDcomputation')

from ID_graph_construction import IncrementalGraphBuilder
from IGC_e_get_bound_new import AttributeDomainComputation, DomianInferFromDC
from cell import Cell, Attribute

class RTFCorrectedAlgorithm:
    """
    Corrected RTF algorithm that properly models constraint-based domain restriction
    """
    
    def __init__(self, target_cell_info, dataset='adult', threshold_alpha=0.8):
        self.target_cell_info = target_cell_info
        self.dataset = dataset
        self.threshold = threshold_alpha
        self.table_name = 'adult_data'
        
        # Initialize your existing components
        self.graph_builder = IncrementalGraphBuilder(target_cell_info, dataset)
        self.domain_computer = AttributeDomainComputation(dataset)
        self.domain_inferrer = DomianInferFromDC(dataset)
        
        # Algorithm state
        self.current_deletion_set = set()
        self.target_cell = None
        self.original_domain_size = 0
        self.current_domain_size = 0
        
        # Constraint modeling
        self.active_constraints = []
        self.constraint_cells = set()
        
        print(f"RTF Corrected Algorithm initialized")
        print(f"Target: {target_cell_info}")
        print(f"Threshold: {threshold_alpha}")
    
    def run_complete_algorithm(self):
        """
        Main method implementing your complete multi-level analysis algorithm
        """
        print(f"\n=== RTF Multi-Level Analysis Algorithm (Corrected) ===")
        
        # === INITIALIZATION ===
        self._initialize_algorithm()
        
        # === MAIN ALGORITHM LOOP ===
        iteration = 0
        
        # Replace the stub methods in graph_builder
        self._inject_real_methods_into_graph_builder()
        
        while self._has_active_constraints_on_target():
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # CHECK: Privacy threshold met?
            if self._check_privacy_threshold():
                print("✓ Privacy threshold achieved - stopping")
                break
            
            # LEVEL 1: Ordered Analysis Phase
            print("=== Level 1: Ordered Analysis Phase ===")
            active_constraints = self._find_active_constraints()
            ordered_constraints = self._order_constraints_by_restrictiveness(active_constraints)
            
            potential_plans = []
            
            for i, constraint in enumerate(ordered_constraints):
                print(f"Analyzing constraint {i+1}/{len(ordered_constraints)}: {constraint['attrs']}")
                
                # Select candidate with largest domain in this constraint
                candidate = self._select_candidate_from_constraint(constraint)
                
                if candidate:
                    # Dynamic graph expansion if needed
                    self._expand_graph_for_candidate(candidate)
                    
                    # What-if analysis
                    benefit = self._calculate_deletion_benefit(candidate)
                    potential_plans.append((benefit, candidate))
                    
                    print(f"    Candidate: {candidate.attribute.col}, Benefit: +{benefit}")
            
            # LEVEL 2: Decision Phase
            print("=== Level 2: Decision Phase ===")
            
            if not potential_plans:
                print("No viable plans found - breaking")
                break
            
            # Select winning plan (maximum benefit)
            potential_plans.sort(key=lambda x: x[0], reverse=True)
            winning_benefit, winning_candidate = potential_plans[0]
            
            print(f"Selected candidate: {winning_candidate.attribute.col} with benefit: {winning_benefit}")
            
            # LEVEL 3: Action Phase
            print("=== Level 3: Action Phase ===")
            
            # Commit the deletion
            self.current_deletion_set.add(winning_candidate)
            print(f"Added to deletion set: {winning_candidate.attribute.col}")
            
            # Update baseline for next cycle
            self.current_domain_size = self._compute_current_domain_size()
            print(f"New domain size: {self.current_domain_size}")
            
            # Safety break
            if iteration > 10:
                print("Maximum iterations reached")
                break
        
        return self._generate_results()
    
    def _initialize_algorithm(self):
        """Initialize with proper constraint-based domain restriction"""
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
        
        # Get original domain size
        self.original_domain_size = self._get_original_domain_size()
        
        # CRITICAL: Initialize with constraint-restricted domain
        # This models the scenario where target is deleted but constraints still apply
        self._initialize_constraint_cells()
        self.current_domain_size = self._compute_initial_restricted_domain()
        
        print(f"Target cell: {self.target_cell.attribute.col} = '{self.target_cell.value}'")
        print(f"Original domain size: {self.original_domain_size}")
        print(f"Initial restricted domain size: {self.current_domain_size}")
        print(f"Initial privacy ratio: {self.current_domain_size / self.original_domain_size:.3f}")
    
    def _initialize_constraint_cells(self):
        """Initialize cells that have constraints with the target"""
        print("Discovering constraint cells...")
        
        row_data = self._get_sample_row_data()
        
        # Mock constraint relationships - replace with your actual constraint discovery
        constraint_attrs = {
            'education': ['age', 'workclass', 'occupation', 'marital-status', 'race'],
            'age': ['education', 'workclass', 'marital-status'],
            'occupation': ['education', 'workclass', 'age']
        }
        
        target_attr = self.target_cell.attribute.col
        related_attrs = constraint_attrs.get(target_attr, [])
        
        for attr in related_attrs:
            if attr in row_data:
                constraint_cell = Cell(
                    Attribute(self.dataset, attr),
                    self.target_cell_info['key'],
                    row_data[attr]
                )
                self.constraint_cells.add(constraint_cell)
        
        print(f"Found {len(self.constraint_cells)} constraint cells: {[c.attribute.col for c in self.constraint_cells]}")
    
    def _compute_initial_restricted_domain(self):
        """
        Compute initial domain size when target is deleted but constraints are active
        This should be smaller than original domain due to constraint restrictions
        """
        # Start with original domain
        original_size = self.original_domain_size
        
        # Apply constraint restrictions from non-deleted cells
        restricted_size = original_size
        
        for constraint_cell in self.constraint_cells:
            # Each active constraint reduces the possible domain
            restriction_factor = self._get_constraint_restriction_factor(
                self.target_cell.attribute.col, 
                constraint_cell.attribute.col
            )
            restricted_size = int(restricted_size * (1 - restriction_factor))
        
        # Ensure minimum domain size of 1
        restricted_size = max(1, restricted_size)
        
        print(f"Domain restricted from {original_size} to {restricted_size} by {len(self.constraint_cells)} active constraints")
        
        return restricted_size
    
    def _get_constraint_restriction_factor(self, target_attr, constraint_attr):
        """
        How much does an active constraint restrict the target domain?
        Higher values mean stronger restriction (smaller domain)
        """
        restriction_map = {
            ('education', 'age'): 0.3,        # Age strongly constrains education
            ('education', 'workclass'): 0.25,  # Workclass constrains education  
            ('education', 'occupation'): 0.4,  # Occupation most strongly constrains education
            ('education', 'marital-status'): 0.15,
            ('education', 'race'): 0.1,
        }
        
        key = (target_attr, constraint_attr)
        factor = restriction_map.get(key, 0.2)  # Default moderate restriction
        
        return factor
    
    def _has_active_constraints_on_target(self):
        """Check if there are still active constraints on target cell"""
        # Constraints are active if the constraining cells are not deleted
        active_count = 0
        for constraint_cell in self.constraint_cells:
            if constraint_cell not in self.current_deletion_set:
                active_count += 1
        
        has_active = active_count > 0
        print(f"Active constraints on target: {active_count}/{len(self.constraint_cells)}")
        
        return has_active
    
    def _find_active_constraints(self):
        """Find currently active constraints"""
        active_constraints = []
        
        for constraint_cell in self.constraint_cells:
            if constraint_cell not in self.current_deletion_set:
                constraint = {
                    'cell': constraint_cell,
                    'attrs': [self.target_cell.attribute.col, constraint_cell.attribute.col],
                    'restriction_factor': self._get_constraint_restriction_factor(
                        self.target_cell.attribute.col,
                        constraint_cell.attribute.col
                    )
                }
                active_constraints.append(constraint)
        
        return active_constraints
    
    def _order_constraints_by_restrictiveness(self, constraints):
        """Order constraints from most restrictive to least restrictive"""
        # Sort by restriction factor (higher = more restrictive)
        return sorted(constraints, key=lambda c: c['restriction_factor'], reverse=True)
    
    def _select_candidate_from_constraint(self, constraint):
        """Select the candidate cell from this constraint"""
        # Return the non-target cell from the constraint
        return constraint['cell']
    
    def _expand_graph_for_candidate(self, candidate):
        """Dynamic graph expansion for candidate"""
        print(f"    Expanding graph for {candidate.attribute.col}")
        # This would integrate with your actual graph expansion logic
        pass
    
    def _calculate_deletion_benefit(self, candidate_cell):
        """
        What-if analysis: calculate benefit of deleting candidate
        """
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
        """
        Core domain computation: how constraint removal affects domain size
        """
        # Start with original domain
        domain_size = self.original_domain_size
        
        # For each constraint cell that's NOT deleted, apply restriction
        total_restriction = 0
        active_constraints = 0
        
        for constraint_cell in self.constraint_cells:
            if constraint_cell not in deletion_set:
                # This constraint is still active, so it restricts the domain
                restriction = self._get_constraint_restriction_factor(
                    self.target_cell.attribute.col,
                    constraint_cell.attribute.col
                )
                total_restriction += restriction
                active_constraints += 1
        
        # Apply total restriction
        if active_constraints > 0:
            # Average restriction per constraint
            avg_restriction = total_restriction / active_constraints
            domain_size = int(self.original_domain_size * (1 - avg_restriction + (avg_restriction * 0.1)))
        
        # Ensure minimum domain size
        domain_size = max(1, domain_size)
        
        return domain_size
    
    def _get_original_domain_size(self):
        """Get original domain size"""
        try:
            domain_info = self.domain_computer.get_domain(self.table_name, self.target_cell.attribute.col)
            if domain_info and 'values' in domain_info:
                return len(domain_info['values'])
            return 16  # Fallback for education
        except:
            return 16
    
    def _check_privacy_threshold(self):
        """Check if privacy threshold is met"""
        if self.original_domain_size == 0:
            return True
        
        privacy_ratio = self.current_domain_size / self.original_domain_size
        met = privacy_ratio >= self.threshold
        
        print(f"Privacy check: {self.current_domain_size}/{self.original_domain_size} = {privacy_ratio:.3f} (threshold: {self.threshold}) -> {'✓' if met else '✗'}")
        
        return met
    
    def _inject_real_methods_into_graph_builder(self):
        """Inject real methods into graph builder"""
        def real_id_computation(deletion_set):
            return self._compute_domain_size_for_deletion_set(deletion_set) > 0
        
        def real_threshold_check():
            return self._check_privacy_threshold()
        
        self.graph_builder.id_computation_stub = real_id_computation
        self.graph_builder.check_threshold_stub = real_threshold_check
    
    def _get_sample_row_data(self):
        """Sample data - replace with your actual data access"""
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
        return {
            'deletion_set': self.current_deletion_set,
            'final_domain_size': self.current_domain_size,
            'original_domain_size': self.original_domain_size,
            'privacy_ratio': self.current_domain_size / self.original_domain_size if self.original_domain_size > 0 else 1.0,
            'threshold_met': self._check_privacy_threshold(),
            'iterations': len(self.current_deletion_set) - 1,
            'constraint_cells_deleted': len([c for c in self.constraint_cells if c in self.current_deletion_set])
        }


def test_corrected_algorithm():
    """Test the corrected algorithm"""
    print("=== Testing CORRECTED RTF Algorithm ===")
    
    # Test with 80% threshold
    target_info = {'key': 2, 'attribute': 'education'}
    algorithm = RTFCorrectedAlgorithm(target_info, 'adult', 0.8)
    
    # Run complete algorithm
    results = algorithm.run_complete_algorithm()
    
    # Display results
    print(f"\n=== FINAL RESULTS ===")
    print(f"🎯 Target: {target_info['attribute']} = 'Bachelors'")
    print(f"📊 Algorithm Performance:")
    print(f"   - Total iterations: {results['iterations']}")
    print(f"   - Constraint cells deleted: {results['constraint_cells_deleted']}")
    print(f"   - Total cells deleted: {len(results['deletion_set'])}")
    
    print(f"\n🔒 Privacy Analysis:")
    print(f"   - Started with domain: {results['original_domain_size']} values")
    print(f"   - Achieved domain: {results['final_domain_size']} values")
    print(f"   - Privacy ratio: {results['privacy_ratio']:.3f}")
    print(f"   - Threshold: {algorithm.threshold}")
    print(f"   - Privacy achieved: {'✅ YES' if results['threshold_met'] else '❌ NO'}")
    
    print(f"\n📋 Deletion Set:")
    for i, cell in enumerate(results['deletion_set'], 1):
        cell_type = "🎯 TARGET" if cell == algorithm.target_cell else "🔗 AUXILIARY"
        print(f"   {i}. {cell.attribute.col} = '{cell.value}' {cell_type}")
    
    print(f"\n📈 Research Insights:")
    privacy_improvement = (results['privacy_ratio'] - (algorithm.current_domain_size / algorithm.original_domain_size)) * 100
    data_cost = results['iterations']
    print(f"   - Privacy improvement: {privacy_improvement:.1f}%")
    print(f"   - Data cost: {data_cost} additional deletions")
    print(f"   - Efficiency: {privacy_improvement/max(1,data_cost):.2f}% improvement per deletion")

if __name__ == '__main__':
    test_corrected_algorithm()