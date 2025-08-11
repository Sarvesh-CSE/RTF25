"""
RTF Multi-Level Analysis Package
================================
Right-to-be-Forgotten privacy protection through strategic cell deletion.

This package implements the complete multi-level analysis strategy for
achieving privacy protection while minimizing data utility loss.

Author: Your Name
Version: 1.0.0
"""

# from .multi_level_optimizer import RTFCorrectedAlgorithm as RTFMultiLevelOptimizer
from .config import get_database_config, get_dataset_info, list_available_datasets

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    'RTFMultiLevelOptimizer',
    'get_database_config',
    'get_dataset_info', 
    'list_available_datasets'
]