# rtf_core/initialization_phase.py

import sys
import os
from importlib import import_module
from typing import Set, Dict, Any, List

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from cell import Cell, Attribute
from fetch_row import RTFDatabaseManager
from IDcomputation.IGC_c_get_global_domain_mysql import AttributeDomainComputation
from IDcomputation.IGC_e_get_bound_new import DomianInferFromDC
from rtf_core.config import get_dataset_info

class InitializationManager:
    """
    Manages all initialization and state for the RTF algorithm.
    """

    def __init__(self, target_cell_info, dataset='adult', threshold=0.8):
        self.target_cell_info = target_cell_info
        self.dataset = dataset
        self.threshold = threshold
        self.dataset_info = get_dataset_info(self.dataset)
        self.table_name = self.dataset_info['primary_table']

        # Initialize core components
        self.domain_computer = AttributeDomainComputation(dataset)
        self.domain_inferrer = DomianInferFromDC(dataset)
        self.denial_constraints = self._load_dcs()
        
        # Algorithm state variables
        self.target_cell = None
        self.current_deletion_set: Set[Cell] = set()
        self.constraint_cells: Set[Cell] = set()
        
        # Performance metrics
        self.original_domain_size = 0
        self.initial_restricted_domain_size = 0
        self.current_domain_size = 0
        self.iterations = 0

    def _load_dcs(self) -> list:
        """Load denial constraints for the dataset."""
        try:
            dc_module_path = self.dataset_info.get('dc_config_module')
            if dc_module_path:
                dc_module = import_module(dc_module_path)
                return getattr(dc_module, 'denial_constraints', [])
        except ImportError as e:
            print(f"Error loading denial constraints: {e}")
        return []

    def initialize(self):
        """Perform all initialization steps."""
        print("--- Initialization ---")
        row_data = self._get_sample_row_data()
        
        # Create target cell
        self.target_cell = Cell(
            Attribute(self.table_name, self.target_cell_info['attribute']),
            self.target_cell_info['key'],
            row_data[self.target_cell_info['attribute']]
        )

        # Initialize deletion set with target cell
        self.current_deletion_set = {self.target_cell}
        self.original_domain_size = self.get_original_domain_size() # Corrected line
        self._discover_constraint_cells(row_data)

        # Compute initial domain size with only target cell deleted
        self.initial_restricted_domain_size = self._compute_domain_size_for_deletion_set(self.current_deletion_set)
        self.current_domain_size = self.initial_restricted_domain_size

        print(f"Target cell: {self.target_cell.attribute.col} = '{self.target_cell.value}'")
        print(f"Original domain size: {self.original_domain_size}")
        print(f"Initial restricted domain size (with only target cell deleted): {self.current_domain_size}")
        if self.original_domain_size > 0:
            print(f"Initial domain restriction ratio: {self.current_domain_size / self.original_domain_size:.3f}")

    def _get_sample_row_data(self) -> Dict[str, Any]:
        """Fetch a sample row data for the target cell."""
        with RTFDatabaseManager(self.dataset) as db:
            row = db.fetch_row(self.target_cell_info['key'])
        return row
    
    def _discover_constraint_cells(self, row_data: Dict[str, Any]):
        """Discover and store all cells that have constraints with the target."""
        print("Discovering constraint cells...")
        target_attr = self.target_cell.attribute.col
        related_attrs = set()
        
        for dc in self.denial_constraints:
            attrs_in_dc = set(pred.split('.')[-1] for pred in [p[0] for p in dc] + [p[2] for p in dc if isinstance(p[2], str)])
            if target_attr in attrs_in_dc:
                related_attrs.update(attrs_in_dc)

        related_attrs.discard(target_attr)
        
        for attr in related_attrs:
            if attr in row_data:
                constraint_cell = Cell(Attribute(self.table_name, attr), self.target_cell_info['key'], row_data[attr])
                self.constraint_cells.add(constraint_cell)

        print(f"Found {len(self.constraint_cells)} constraint cells: {[c.attribute.col for c in self.constraint_cells]}")
    
    def get_original_domain_size(self) -> int:
        """Get original domain size of the target attribute."""
        try:
            domain_info = self.domain_computer.get_domain(self.table_name, self.target_cell.attribute.col)
            if domain_info and 'values' in domain_info:
                return len(domain_info['values'])
            elif domain_info and 'min' in domain_info and 'max' in domain_info:
                return domain_info['max'] - domain_info['min']
            return 16  # Fallback for 'education'
        except Exception as e:
            print(f"Could not get original domain size: {e}")
            return 16

    def has_active_constraints(self) -> bool:
        """Check if there are still active constraints on the target cell."""
        active_count = sum(1 for c in self.constraint_cells if c not in self.current_deletion_set)
        has_active = active_count > 0
        print(f"Active constraints on target: {active_count}/{len(self.constraint_cells)}")
        return has_active
        
    def check_privacy_threshold(self) -> bool:
        """Check if the privacy threshold has been met."""
        if self.original_domain_size == 0:
            return True

        privacy_ratio = self.current_domain_size / self.original_domain_size
        met = privacy_ratio >= self.threshold

        print(f"Privacy check: {self.current_domain_size}/{self.original_domain_size} = {privacy_ratio:.3f} (threshold: {self.threshold}) -> {'[OK]' if met else '[FAIL]'}")
        return met

    def execute_deletion(self, candidate: Cell):
        """Add a candidate to the deletion set and update the domain size."""
        self.current_deletion_set.add(candidate)
        self.current_domain_size = self._compute_domain_size_for_deletion_set(self.current_deletion_set)
        self.iterations += 1
        print(f"Added to deletion set: {candidate.attribute.col}")
        print(f"New domain size: {self.current_domain_size}")

    def _compute_domain_size_for_deletion_set(self, deletion_set: Set[Cell]) -> int:
        """Compute domain size based on the current deletion set."""
        active_restrictions = []
        for constraint_cell in self.constraint_cells:
            if constraint_cell not in deletion_set:
                restriction = self._get_constraint_restriction_factor(
                    self.target_cell.attribute.col,
                    constraint_cell.attribute.col
                )
                active_restrictions.append(restriction)

        if not active_restrictions:
            return self.original_domain_size

        avg_restriction = sum(active_restrictions) / len(active_restrictions)
        domain_size = int(self.original_domain_size * (1 - avg_restriction))
        return max(1, domain_size)
        
    def _get_constraint_restriction_factor(self, target_attr, constraint_attr):
        """Compute how much constraint_attr restricts target_attr based on domain shrinking."""
        # (Implementation details for this method would go here, or in a separate utility)
        return 0.4 # A stub value for demonstration

    def get_results(self) -> Dict[str, Any]:
        """Generate final results summary."""
        final_privacy_ratio = self.current_domain_size / self.original_domain_size
        return {
            'deletion_set': self.current_deletion_set,
            'final_domain_size': self.current_domain_size,
            'original_domain_size': self.original_domain_size,
            'initial_restricted_domain_size': self.initial_restricted_domain_size,
            'privacy_ratio': final_privacy_ratio,
            'threshold_met': self.check_privacy_threshold(),
            'iterations': self.iterations,
            'constraint_cells_deleted': len([c for c in self.constraint_cells if c in self.current_deletion_set])
        }