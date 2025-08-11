# rtf_core/decision_phase.py

from typing import Dict, Any, List
from .initialization import InitializationManager

class DecisionPhase:
    """
    Implements the "Decision Phase" of the RTF algorithm.
    """
    def __init__(self, init_manager: InitializationManager):
        self.init_manager = init_manager

    def run(self, potential_plans: List[Dict[str, Any]]) -> Any:
        """
        Selects the single best candidate for deletion from the list of plans.
        """
        print("=== Level 2: Decision Phase ===")
        if not potential_plans:
            print("No viable plans found - skipping deletion.")
            return None

        # Sort plans by benefit in descending order
        potential_plans.sort(key=lambda x: x['benefit'], reverse=True)
        
        winning_plan = potential_plans[0]
        winning_benefit = winning_plan['benefit']
        winning_candidate = winning_plan['candidate']

        print(f"Selected candidate: {winning_candidate.attribute.col} with benefit: {winning_benefit}")
        return winning_candidate