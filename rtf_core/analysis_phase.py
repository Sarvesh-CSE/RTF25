# rtf_core/analysis_phase.py

from typing import Dict, Any, List
from .initialization_phase import InitializationManager # Corrected import

class OrderedAnalysisPhase:
    """
    Implements the "Ordered Analysis Phase" of the RTF algorithm.
    """
    def __init__(self, init_manager: InitializationManager):
        self.init_manager = init_manager

    def run(self) -> List[Dict[str, Any]]:
        """
        Finds and analyzes potential deletion plans.
        Returns a list of potential plans (benefits and candidates).
        """
        print("=== Level 1: Ordered Analysis Phase ===")
        active_constraints = self._find_active_constraints()
        ordered_constraints = self._order_constraints_by_restrictiveness(active_constraints)

        potential_plans = []
        for i, constraint in enumerate(ordered_constraints):
            print(f"Analyzing constraint {i+1}/{len(ordered_constraints)}: {constraint['attrs']}")

            candidate = self._select_candidate_from_constraint(constraint)
            if candidate:
                benefit = self._calculate_deletion_benefit(candidate)
                potential_plans.append({
                    'benefit': benefit,
                    'candidate': candidate,
                    'constraint': constraint
                })
                print(f"    Candidate: {candidate.attribute.col}, Benefit: +{benefit}")

        return potential_plans

    def _find_active_constraints(self) -> List[Dict[str, Any]]:
        """Find currently active constraints."""
        active_constraints = []
        for constraint_cell in self.init_manager.constraint_cells:
            if constraint_cell not in self.init_manager.current_deletion_set:
                restriction_factor = self.init_manager._get_constraint_restriction_factor(
                    self.init_manager.target_cell.attribute.col,
                    constraint_cell.attribute.col
                )
                active_constraints.append({
                    'cell': constraint_cell,
                    'attrs': [self.init_manager.target_cell.attribute.col, constraint_cell.attribute.col],
                    'restriction_factor': restriction_factor
                })
        return active_constraints

    def _order_constraints_by_restrictiveness(self, constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Order constraints from most restrictive to least restrictive."""
        return sorted(constraints, key=lambda c: c['restriction_factor'], reverse=True)

    def _select_candidate_from_constraint(self, constraint: Dict[str, Any]) -> Any:
        """Select the candidate cell from this constraint."""
        return constraint['cell']

    def _calculate_deletion_benefit(self, candidate_cell: Any) -> float:
        """What-if analysis: calculate benefit of deleting the candidate."""
        current_size = self.init_manager.current_domain_size
        hypothetical_deletion_set = self.init_manager.current_deletion_set.union({candidate_cell})
        hypothetical_size = self.init_manager._compute_domain_size_for_deletion_set(hypothetical_deletion_set)
        return hypothetical_size - current_size