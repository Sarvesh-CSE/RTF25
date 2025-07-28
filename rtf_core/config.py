"""
Enhanced Configuration for RTF (Right to Be Forgotten) Project
============================================================
Step 1: Adding centralized configuration
for datasets, databases, tables, keys, DCs, and domain computation.
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
    'output': PROJECT_ROOT / 'output',  # Your existing OUTPUT_DIR
    'logs': PROJECT_ROOT / 'logs',
}

# Create output directories if they don't exist
for path in [PATHS['output'], PATHS['logs']]:
    path.mkdir(exist_ok=True)

# ============================================================================
# DATABASE CONFIGURATION (Centralizing from multiple files)
# ============================================================================

# Base database configuration (from your existing config and found patterns)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'uci@dbh@2084',  # Centralized - was hardcoded in 5+ files
    'ssl_disabled': True,
    'charset': 'utf8mb4'
}

# ============================================================================
# COMPREHENSIVE DATASET CONFIGURATIONS
# ============================================================================

# Complete dataset configurations - datasets, databases, tables, keys, DCs, domains
DATASETS = {
    'adult': {
        'name': 'adult',
        'database_name': 'adult',
        'description': 'UCI Adult Census Income Dataset',
        'primary_table': 'adult_data',
        'key_column': 'id',
        'tables': ['adult_data'],
        'dc_config_module': 'DCandDelset.dc_configs.topAdultDCs_parsed',
        'dc_file': 'topAdultDCs_parsed.py',
        'dc_raw_file': 'topAdultDCs',
        'data_generation_dir': 'adult',
        'domain_file': 'adult_domain_map.json',
        'test_attribute': 'education',  # <- ADD THIS LINE
    },
    
    'tax': {
        'name': 'tax',
        'database_name': 'tax',
        'description': 'Synthetic Tax Records Dataset',
        'primary_table': 'tax_data',
        'key_column': 'id',
        'tables': ['tax_data'],
        'dc_config_module': 'DCandDelset.dc_configs.topTaxDCs_parsed',
        'dc_file': 'topTaxDCs_parsed.py',
        'dc_raw_file': 'topTaxDCs',
        'domain_file': 'tax_domain_map.json',
        'test_attribute': 'salary',  # <- ADD THIS LINE
    },
    
    'hospital': {
        'name': 'hospital',
        'database_name': 'hospital',
        'description': 'Hospital Quality Dataset',
        'primary_table': 'hospital_data',
        'key_column': 'id',
        'tables': ['hospital_data'],
        'dc_config_module': 'DCandDelset.dc_configs.topHospitalDCs_parsed',
        'dc_file': 'topHospitalDCs_parsed.py',
        'dc_raw_file': 'topHospitalDCs',
        'domain_file': 'hospital_domain_map.json',
        'test_attribute': 'City',  # <- ADD THIS LINE
    },
    
    'ncvoter': {
        'name': 'ncvoter',
        'database_name': 'ncvoter',
        'description': 'North Carolina Voter Registration Dataset',
        'primary_table': 'ncvoter_data',
        'key_column': 'id',
        'tables': ['ncvoter_data'],
        'dc_config_module': 'DCandDelset.dc_configs.topNCVoterDCs_parsed',
        'dc_file': 'topNCVoterDCs_parsed.py',
        'dc_raw_file': 'topNCVoterDCs',
        'domain_file': 'ncvoter_domain_map.json',
        'test_attribute': [],
    },
    
    'airport': {
        'name': 'airport',
        'database_name': 'airport',
        'description': 'Global Airports Dataset',
        'primary_table': 'airports',
        'key_column': 'id',
        'tables': ['airports'],
        'dc_config_module': 'DCandDelset.dc_configs.topAirportDCs_parsed',
        'dc_file': 'topAirportDCs_parsed.py',
        'dc_raw_file': 'topAirportDCs',
        'domain_file': 'airport_domain_map.json',
        'test_attribute': 'country',  
    },
    
    'rtf25': {
        'name': 'rtf25',
        'database_name': 'RTF25',
        'description': 'RTF25 Synthetic Enterprise Dataset',
        'primary_table': 'Tax',
        'key_column': 'EId',
        'tables': ['Employee', 'Payroll', 'Tax'],
        'dc_config_module': None,  # Add when available
        'dc_file': 'rtf25_dcs.py',
        'dc_raw_file': 'rtf25_dcs',
        'domain_file': 'RTF25_domain_map.json',
    },
    
    'tpchdb': {
        'name': 'tpchdb',
        'database_name': 'tpchdb',
        'description': 'TPC-H Benchmark Database',
        'primary_table': 'lineitem',
        'key_column': 'l_orderkey',
        'tables': ['region', 'nation', 'supplier', 'customer', 'part', 'partsupp', 'orders', 'lineitem'],
        'dc_config_module': None,  # Add when available
        'dc_file': 'tpch_dcs.py',
        'dc_raw_file': 'tpch_dcs',
        'domain_file': 'tpchdb_domain_map.json',
    },
}

# ============================================================================
# ALGORITHM PARAMETERS AND DEFAULTS
# ============================================================================

# Default target EID (from your existing config)
DEFAULT_TARGET_EID = 2

# Algorithm defaults found in various files
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
# UTILITY FUNCTIONS
# ============================================================================

def list_available_datasets():
    """Get list of available dataset names."""
    return list(DATASETS.keys())

def validate_dataset(dataset_name):
    """Validate that a dataset configuration is complete and files exist."""
    if dataset_name not in DATASETS:
        return False, f"Dataset '{dataset_name}' not found in configuration"
    
    dataset = DATASETS[dataset_name]
    issues = []
    
    # Check if DC config file exists (if specified)
    if dataset.get('dc_file'):
        dc_path = get_dc_config_path(dataset_name)
        if not dc_path.exists():
            issues.append(f"DC config file not found: {dc_path}")
    
    # Check if raw DC file exists (if specified)
    if dataset.get('dc_raw_file'):
        dc_raw_path = get_dc_raw_path(dataset_name)
        if not dc_raw_path.exists():
            issues.append(f"Raw DC file not found: {dc_raw_path}")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, "Dataset configuration is valid"

# ============================================================================
# TESTING AND VALIDATION
# ============================================================================

if __name__ == "__main__":
    print("Enhanced RTF Configuration")
    print("=" * 60)
    
    # Show available datasets
    datasets = list_available_datasets()
    print(f"\nAvailable datasets ({len(datasets)}): {datasets}")
    
    # Test core functions for each dataset
    print(f"\nDataset Information:")
    for dataset in datasets[:3]:  # Test first 3
        try:
            db_config = get_database_config(dataset)
            dataset_info = get_dataset_info(dataset)
            
            print(f"\n{dataset.upper()}:")
            print(f"  Database: {db_config['database']}")
            print(f"  Primary Table: {get_primary_table(dataset)}")
            print(f"  Key Column: {get_key_column(dataset)}")
            print(f"  All Tables: {get_all_tables(dataset)}")
            print(f"  Domain File: {get_domain_file_path(dataset).name}")
            print(f"  DC File: {get_dc_config_path(dataset).name}")
            
            # Validate dataset
            is_valid, message = validate_dataset(dataset)
            print(f"  Valid: {is_valid} ({message})")
            
        except Exception as e:
            print(f"  {dataset} -> ERROR: {e}")
    
    # Test backward compatibility
    print(f"\nBackward Compatibility:")
    print(f"  DATABASES: {DATABASES}")
    print(f"  OUTPUT_DIR: {OUTPUT_DIR}")
    print(f"  DEFAULT_TARGET_EID: {DEFAULT_TARGET_EID}")
    
    print(f"\nConfiguration ready for gradual migration!")