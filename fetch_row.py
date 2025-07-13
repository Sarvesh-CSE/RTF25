#!/usr/bin/env python3
"""
Compact Fetch Row Logic - Independent Target Tuple Retrieval
===========================================================

Usage:
    from fetch_row import fetch_row
    
    row = fetch_row(2)              # Default 'adult' dataset
    row = fetch_row(2, 'tax')       # Specific dataset
    education = fetch_row(2)['education']  # Get specific value
"""

import mysql.connector
import sys
import os
from typing import Dict, Any

# Add project root for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import central config
from config import get_database_config, get_dataset_info


def fetch_row(target_key: int, dataset: str = 'adult') -> Dict[str, Any]:
    """
    Fetch target tuple from database.
    
    Args:
        target_key: Primary key of the target row
        dataset: Dataset name ('adult', 'tax', 'hospital', etc.)
        
    Returns:
        Dictionary with all column values for the target row
        
    Raises:
        ValueError: If target_key not found
        RuntimeError: If database connection fails
    """
    try:
        # Get config for dataset
        db_config = get_database_config(dataset)
        dataset_info = get_dataset_info(dataset)
        
        # Connect and query
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        query = f"SELECT * FROM {dataset_info['primary_table']} WHERE {dataset_info['key_column']} = %s LIMIT 1"
        cursor.execute(query, (target_key,))
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if row is None:
            raise ValueError(f"No row found with {dataset_info['key_column']}={target_key}")
        
        return row
        
    except mysql.connector.Error as e:
        raise RuntimeError(f"Database error: {e}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test fetch_row
    row = fetch_row(2)
    print(f"Row 2 education: {row.get('education', 'N/A')}")
    
    # Test different dataset
    try:
        tax_row = fetch_row(2, 'tax')
        print(tax_row)
        print(f"Tax row 2: ✓")
    except Exception as e:
        print(f"Tax row 2: ✗ ({e})")