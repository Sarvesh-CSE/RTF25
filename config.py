"""
Configuration for existing RTF codebase
"""

import os

# Database Configuration (from existing db_wrapper.py)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'uci@dbh@2084',
    'database': 'adult'  # Default database
}

# Available databases from your codebase
DATABASES = {
    'adult': 'adult',
    'airport': 'airport',
    'ncvoter': 'ncvoter', 
    'tax': 'tax',
    'hospital': 'hospital'
}

# DC Configuration files (from DCandDelset/dc_configs/)
DC_CONFIGS = {
    'adult': 'DCandDelset.dc_configs.topAdultDCs_parsed',
    'airport': 'DCandDelset.dc_configs.topAirportDCs_parsed',
    'ncvoter': 'DCandDelset.dc_configs.topNCVoterDCs_parsed', 
    'tax': 'DCandDelset.dc_configs.topTaxDCs_parsed',
    'hospital': 'DCandDelset.dc_configs.topHospitalDCs_parsed'
}

# Default target EID (used in existing code)
DEFAULT_TARGET_EID = 2

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)