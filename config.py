"""
Complete RTF Configuration
=========================
Standalone configuration that provides all needed functions
without circular imports.
"""

import os
from pathlib import Path

# ============================================================================
# PROJECT STRUCTURE AND PATHS
# ============================================================================

# Project root directory (where this config.py file is located)
PROJECT_ROOT = Path(__file__).parent

# Key directories in your RTF project
PATHS = {
    'project_root': PROJECT_ROOT,
    'dc_configs': PROJECT_ROOT / 'DCandDelset' / 'dc_configs',
    'dc_raw': PROJECT_ROOT / 'DCandDelset' / 'dc_configs' / 'raw_constraints',
    'data_generation': PROJECT_ROOT / 'DataGeneration',
    'inference_graphs': PROJECT_ROOT / 'InferenceGraph', 
    'id_computation': PROJECT_ROOT / 'IDcomputation',
    'output': PROJECT_ROOT / 'output',
    'logs': PROJECT_ROOT / 'logs',
}

# Create output directories if they don't exist
for path in [PATHS['output'], PATHS['logs']]:
    if not path.exists():
        path.mkdir(exist_ok=True)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Base database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'uci@dbh@2084',
    'ssl_disabled': True,
    'charset': 'utf8mb4'
}

# ============================================================================
# COMPREHENSIVE DATASET CONFIGURATIONS
# ============================================================================

# Complete dataset configurations
DATASETS = {
    'adult': {
        'name': 'adult',
        'database_name': 'adult',
        'primary_table': 'adult_data',
        'key_column': 'id',
        'tables': ['adult_data'],
        'domain_file': 'adult_domain_map.json',
        'dc_file': 'topAdultDCs_parsed.py',
        'dc_raw_file': 'topAdultDCs',
        'dc_config_module': 'DCandDelset.dc_configs.topAdultDCs_parsed'
    },
    'tax': {
        'name': 'tax',
        'database_name': 'tax',
        'primary_table': 'tax_data',
        'key_column': 'id',
        'tables': ['tax_data'],
        'domain_file': 'tax_domain_map.json',
        'dc_file': 'tax_dcs.py',
        'dc_raw_file': 'tax_dcs',
        'dc_config_module': None
    },
    'hospital': {
        'name': 'hospital',
        'database_name': 'hospital',
        'primary_table': 'hospital_data',
        'key_column': 'id',
        'tables': ['hospital_data'],
        'domain_file': 'hospital_domain_map.json',
        'dc_file': 'hospital_dcs.py',
        'dc_raw_file': 'hospital_dcs',
        'dc_config_module': None
    },
    'ncvoter': {
        'name': 'ncvoter',
        'database_name': 'ncvoter',
        'primary_table': 'ncvoter_data',
        'key_column': 'id',
        'tables': ['ncvoter_data'],
        'domain_file': 'ncvoter_domain_map.json',
        'dc_file': 'ncvoter_dcs.py',
        'dc_raw_file': 'ncvoter_dcs',
        'dc_config_module': None
    },
    'airport': {
        'name': 'airport',
        'database_name': 'airport',
        'primary_table': 'airport_data',
        'key_column': 'id',
        'tables': ['airport_data'],
        'domain_file': 'airport_domain_map.json',
        'dc_file': 'airport_dcs.py',
        'dc_raw_file': 'airport_dcs',
        'dc_config_module': None
    },
    'rtf25': {
        'name': 'rtf25',
        'database_name': 'RTF25',
        'primary_table': 'rtf25_data',
        'key_column': 'id',
        'tables': ['rtf25_data'],
        'domain_file': 'rtf25_domain_map.json',
        'dc_file': 'rtf25_dcs.py',
        'dc_raw_file': 'rtf25_dcs',
        'dc_config_module': None
    },
    'tpchdb': {
        'name': 'tpchdb',
        'database_name': 'tpchdb',
        'primary_table': 'customer',
        'key_column': 'custkey',
        'tables': ['customer', 'supplier', 'nation', 'region', 'part', 'partsupp', 'orders', 'lineitem'],
        'domain_file': 'tpchdb_domain_map.json',
        'dc_file': 'tpch_dcs.py',
        'dc_raw_file': 'tpch_dcs',
        'dc_config_module': None
    },
}

# ============================================================================
# ALGORITHM PARAMETERS AND DEFAULTS
# ============================================================================

# Default target EID
DEFAULT_TARGET_EID = 2

# Algorithm defaults
ALGORITHM_DEFAULTS = {
    'default_table': 'adult_data',
    'default_target_column': 'education',
    'default_key_column': 'id',
    'default_key_value': '4',
    'alpha': 0.1,
    'sample_size': 1000,
    'max_iterations': 100,
    'timeout_seconds': 300,
}

# ============================================================================
# CORE HELPER FUNCTIONS
# ============================================================================

def get_database_config(dataset_name):
    """Get database connection configuration for a dataset."""
    if dataset_name not in DATASETS:
        available = list(DATASETS.keys())
        raise ValueError(f"Unknown dataset: {dataset_name}. Available: {available}")
    
    dataset = DATASETS[dataset_name]
    config = DB_CONFIG.copy()
    config['database'] = dataset['database_name']
    return config

def get_dataset_info(dataset_name):
    """Get complete dataset information (database, tables, keys, DCs, domains)."""
    if dataset_name not in DATASETS:
        available = list(DATASETS.keys())
        raise ValueError(f"Unknown dataset: {dataset_name}. Available: {available}")
    
    return DATASETS[dataset_name].copy()

def get_primary_table(dataset_name):
    """Get primary table name for a dataset."""
    return get_dataset_info(dataset_name)['primary_table']

def get_key_column(dataset_name):
    """Get primary key column for a dataset."""
    return get_dataset_info(dataset_name)['key_column']

def get_all_tables(dataset_name):
    """Get all tables for a dataset."""
    return get_dataset_info(dataset_name)['tables']

def list_available_datasets():
    """Get list of available dataset names."""
    return list(DATASETS.keys())

# ============================================================================
# FILE PATH FUNCTIONS (Domains, DCs, etc.)
# ============================================================================

def get_domain_file_path(dataset_name):
    """Get path to computed domain map JSON file for a dataset."""
    dataset = get_dataset_info(dataset_name)
    return PATHS['id_computation'] / dataset['domain_file']

def get_dc_config_path(dataset_name):
    """Get path to parsed denial constraint Python file."""
    dataset = get_dataset_info(dataset_name)
    return PATHS['dc_configs'] / dataset['dc_file']

def get_dc_raw_path(dataset_name):
    """Get path to raw denial constraint file."""
    dataset = get_dataset_info(dataset_name)
    return PATHS['dc_raw'] / dataset['dc_raw_file']

def get_output_file(filename):
    """Get path for output files."""
    return PATHS['output'] / filename

def get_log_file(filename):
    """Get path for log files."""
    return PATHS['logs'] / filename

def get_data_generation_path(dataset_name):
    """Get path to data generation directory for a dataset."""
    dataset = get_dataset_info(dataset_name)
    if 'data_generation_dir' in dataset:
        return PATHS['data_generation'] / dataset['data_generation_dir']
    return PATHS['data_generation']

# ============================================================================
# BACKWARD COMPATIBILITY (Your existing variables)
# ============================================================================

# Keep your existing variables for backward compatibility
DATABASES = {dataset['name']: dataset['database_name'] for dataset in DATASETS.values()}

DC_CONFIGS = {
    name: dataset['dc_config_module'] 
    for name, dataset in DATASETS.items() 
    if dataset['dc_config_module']
}

OUTPUT_DIR = str(PATHS['output'])  # Your existing OUTPUT_DIR as string

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_dataset(dataset_name):
    """Validate that a dataset configuration is complete and files exist."""
    if dataset_name not in DATASETS:
        return False, f"Dataset {dataset_name} not found"
    
    dataset = DATASETS[dataset_name]
    
    # Check required fields
    required_fields = ['name', 'database_name', 'primary_table', 'key_column']
    for field in required_fields:
        if field not in dataset:
            return False, f"Dataset {dataset_name} missing required field: {field}"
    
    return True, "Dataset configuration valid"

# ============================================================================
# EXPORT ALL FUNCTIONS
# ============================================================================

__all__ = [
    # Core configuration
    'DATASETS', 'DB_CONFIG', 'PATHS', 'ALGORITHM_DEFAULTS',
    
    # Main functions
    'get_database_config', 'get_dataset_info', 'list_available_datasets',
    'get_primary_table', 'get_key_column', 'get_all_tables',
    
    # File path functions
    'get_domain_file_path', 'get_dc_config_path', 'get_dc_raw_path',
    'get_output_file', 'get_log_file', 'get_data_generation_path',
    
    # Backward compatibility
    'DATABASES', 'DC_CONFIGS', 'OUTPUT_DIR',
    
    # Utilities
    'validate_dataset', 'DEFAULT_TARGET_EID'
]

# Debug print
print("[OK] Standalone config.py loaded successfully")
