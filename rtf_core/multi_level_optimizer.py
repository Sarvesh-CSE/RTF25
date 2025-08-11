# rtf_core/multi_level_optimizer.py

import sys
import os
from typing import Set, Dict, Any, List

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from cell import Cell, Attribute
from rtf_core.initialization import InitializationManager
from rtf_core.analysis_phase import OrderedAnalysisPhase
from rtf_core.decision_phase import DecisionPhase

class RTFCorrectedAlgorithm:
    """
    Corrected RTF algorithm that orchestrates modular components.
    """

    def __init__(self, target_cell_info, dataset='adult', threshold_alpha=0.8):
        self.init_manager = InitializationManager(target_cell_info, dataset, threshold_alpha)
        self.analysis_phase = OrderedAnalysisPhase(self.init_manager)
        self.decision_phase = DecisionPhase(self.init_manager)
        print("RTF Algorithm initialized")
        print(f"Target: {target_cell_info}")
        print(f"Threshold: {threshold_alpha}")

    def run_complete_algorithm(self):
        """
        Main method implementing your complete multi-level analysis algorithm.
        """
        print(f"\n=== RTF Multi-Level Analysis Algorithm (Corrected) ===")
        
        # Initialization Phase
        self.init_manager.initialize()
        
        # Main Algorithm Loop
        while self.init_manager.has_active_constraints() and not self.init_manager.check_privacy_threshold():
            print(f"\n--- Iteration {self.init_manager.iterations + 1} ---")
            
            # Level 1: Ordered Analysis Phase
            potential_plans = self.analysis_phase.run()
            
            # Level 2: Decision Phase
            winning_candidate = self.decision_phase.run(potential_plans)
            
            # Level 3: Action Phase
            if winning_candidate:
                self.init_manager.execute_deletion(winning_candidate)
            else:
                break
            
            # Safety break
            if self.init_manager.iterations > 10:
                print("Maximum iterations reached")
                break
        
        return self.init_manager.get_results()


def test_corrected_algorithm():
    """Test the corrected algorithm."""
    print("=== Testing CORRECTED RTF Algorithm ===")
    target_info = {'key': 2, 'attribute': 'education'}
    algorithm = RTFCorrectedAlgorithm(target_info, 'adult', 0.8)

    results = algorithm.run_complete_algorithm()

    print(f"\n=== FINAL RESULTS ===")
    print(f"[TARGET] Target: {target_info['attribute']} = 'Bachelors'")
    print(f"[DATA] Algorithm Performance:")
    print(f"   - Total iterations: {results['iterations']}")
    print(f"   - Constraint cells deleted: {results['constraint_cells_deleted']}")
    print(f"   - Total cells deleted: {len(results['deletion_set'])}")

    print(f"\n? Privacy Analysis:")
    print(f"   - Started with domain: {results['original_domain_size']} values")
    print(f"   - Achieved domain: {results['final_domain_size']} values")
    print(f"   - Privacy ratio: {results['privacy_ratio']:.3f}")
    print(f"   - Threshold: {algorithm.init_manager.threshold}")
    print(f"   - Privacy achieved: {'[SUCCESS] YES' if results['threshold_met'] else '[ERROR] NO'}")

    print(f"\n[LIST] Deletion Set:")
    for i, cell in enumerate(results['deletion_set'], 1):
        cell_type = "[TARGET] TARGET" if cell == algorithm.init_manager.target_cell else "? AUXILIARY"
        print(f"   {i}. {cell.attribute.col} = '{cell.value}' {cell_type}")

    print(f"\n[GROWTH] Research Insights:")
    if algorithm.init_manager.original_domain_size > 0:
        initial_privacy_ratio = results['initial_restricted_domain_size'] / results['original_domain_size']
        privacy_improvement = (results['privacy_ratio'] - initial_privacy_ratio) * 100
        data_cost = results['iterations']
        print(f"   - Privacy improvement: {privacy_improvement:.1f}%")
        print(f"   - Data cost: {data_cost} additional deletions")
        if data_cost > 0:
            print(f"   - Efficiency: {privacy_improvement/data_cost:.2f}% improvement per deletion")

if __name__ == '__main__':
    test_corrected_algorithm()