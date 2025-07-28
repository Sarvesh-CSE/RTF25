#!/usr/bin/env python3
"""
Compact Repository-Level Database Manager
========================================

Usage:
    from fetch_row import RTFDatabaseManager
    
    with RTFDatabaseManager('adult') as db:
        row = db.fetch_row(2)
        education = db.fetch_row(2)['education']
"""

import mysql.connector
import sys
import os
from typing import Dict, Any

# Add project root for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_database_config, get_dataset_info


class RTFDatabaseManager:
    """Repository-level database connection manager."""
    
    def __init__(self, dataset: str = 'adult'):
        self.dataset = dataset
        self.dataset_info = get_dataset_info(dataset)
        self.db_config = get_database_config(dataset)
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        """Open connection."""
        self.connection = mysql.connector.connect(**self.db_config)
        self.cursor = self.connection.cursor(dictionary=True)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def fetch_row(self, target_key: int) -> Dict[str, Any]:
        """Fetch target tuple."""
        query = f"SELECT * FROM {self.dataset_info['primary_table']} WHERE {self.dataset_info['key_column']} = %s LIMIT 1"
        self.cursor.execute(query, (target_key,))
        row = self.cursor.fetchone()
        
        if row is None:
            raise ValueError(f"No row found with {self.dataset_info['key_column']}={target_key}")
        
        return row


if __name__ == "__main__":
    # Test repository-level connection
    with RTFDatabaseManager('adult') as db: 
        # ? __enter__ called: connection opens, cursor created
        row1 = db.fetch_row(2)
        row2 = db.fetch_row(3)
        print(f"Row 2 education: {row1.get('education', 'N/A')}")
        print(f"Row 3 education: {row2.get('education', 'N/A')}")
        # ? LAST LINE OF WITH BLOCK COMPLETES
    # ? __exit__ called: connection closes, cursor destroyed