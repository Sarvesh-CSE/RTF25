"""
Updated Database Wrapper using Central Configuration
==================================================
Step 3: Replace your current db_wrapper.py with this version.

This version uses the central config for:
- Database connections (supports all datasets)
- Dataset-specific table and key information
- Backward compatibility with existing code
"""

import mysql.connector
import sys
import os
from typing import Optional, Dict, Any, List

# Add project root to path for config import
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import from central configuration
from config import (
    get_database_config, get_dataset_info, get_primary_table, 
    get_key_column, get_all_tables, list_available_datasets
)

class DatabaseConfig:
    """Database configuration using central config system."""
    
    def __init__(self, dataset_name: str = 'adult'):
        """
        Initialize database configuration for a specific dataset.
        
        Args:
            dataset_name: Name of the dataset from central configuration
        """
        self.dataset_name = dataset_name
        self.config = get_database_config(dataset_name)
        self.dataset_info = get_dataset_info(dataset_name)
        self.connection = None
        self.cursor = None
        
        print(f"Database config initialized for dataset: {dataset_name}")
        print(f"Database: {self.config['database']}")
        
        # Auto-connect for backward compatibility
        self.connect()

    def connect(self):
        """Establish database connection with dictionary cursor."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            print(f"Connected to database: {self.config['database']}")
        except mysql.connector.Error as e:
            print(f"Database connection failed: {e}")
            raise

    def close(self):
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print(f"Database connection closed")

    def get_primary_table_name(self) -> str:
        """Get the primary table name for this dataset."""
        return self.dataset_info['primary_table']
    
    def get_key_column_name(self) -> str:
        """Get the primary key column name for this dataset."""
        return self.dataset_info['key_column']
    
    def get_all_table_names(self) -> List[str]:
        """Get all table names for this dataset."""
        return self.dataset_info['tables']

class DatabaseWrapper:
    """Enhanced database wrapper using central configuration."""
    
    def __init__(self, dataset_name_or_config):
        """
        Initialize database wrapper.
        
        Args:
            dataset_name_or_config: Either a dataset name (str) or DatabaseConfig object
                                   for backward compatibility
        """
        if isinstance(dataset_name_or_config, str):
            # New way: pass dataset name
            self.dataset_name = dataset_name_or_config
            self.db = DatabaseConfig(dataset_name_or_config)
        elif isinstance(dataset_name_or_config, DatabaseConfig):
            # Backward compatibility: pass DatabaseConfig object
            self.dataset_name = getattr(dataset_name_or_config, 'dataset_name', 'unknown')
            self.db = dataset_name_or_config
        else:
            raise ValueError("dataset_name_or_config must be a string (dataset name) or DatabaseConfig object")

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SQL query and return all results."""
        try:
            self.db.cursor.execute(query, params)
            return self.db.cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Query execution failed: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and return one result."""
        try:
            self.db.cursor.execute(query, params)
            return self.db.cursor.fetchone()  # returns a dict because dictionary=True
        except mysql.connector.Error as e:
            print(f"Query execution failed: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an UPDATE/INSERT/DELETE query and return affected rows."""
        try:
            self.db.cursor.execute(query, params)
            self.db.connection.commit()
            return self.db.cursor.rowcount
        except mysql.connector.Error as e:
            self.db.connection.rollback()
            print(f"Update execution failed: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise

    def get_table_info(self) -> Dict[str, List[str]]:
        """Get information about tables and columns in the database."""
        table_info = {}
        for table_name in self.db.get_all_table_names():
            columns_query = """
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """
            columns = self.execute_query(columns_query, (self.db.config['database'], table_name))
            table_info[table_name] = [col['COLUMN_NAME'] for col in columns]
        
        return table_info

    def get_primary_table(self) -> str:
        """Get the primary table name for this dataset."""
        return self.db.get_primary_table_name()

    def get_key_column(self) -> str:
        """Get the primary key column name for this dataset."""
        return self.db.get_key_column_name()

    def get_all_tables(self) -> List[str]:
        """Get all table names for this dataset."""
        return self.db.get_all_table_names()

    def fetch_row_by_key(self, key_value: Any, table_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a row by its primary key value.
        
        Args:
            key_value: Value of the primary key
            table_name: Table name (defaults to primary table)
        
        Returns:
            Dictionary representing the row, or None if not found
        """
        if table_name is None:
            table_name = self.get_primary_table()
        
        key_column = self.get_key_column()
        
        query = f"SELECT * FROM {table_name} WHERE {key_column} = %s LIMIT 1"
        return self.fetch_one(query, (key_value,))

    def get_row_count(self, table_name: Optional[str] = None) -> int:
        """
        Get the number of rows in a table.
        
        Args:
            table_name: Table name (defaults to primary table)
        
        Returns:
            Number of rows in the table
        """
        if table_name is None:
            table_name = self.get_primary_table()
        
        result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table_name}")
        return result['count'] if result else 0

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        query = """
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        result = self.fetch_one(query, (self.db.config['database'], table_name))
        return result['count'] > 0 if result else False

    def close(self):
        """Close the database connection."""
        self.db.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_database_wrapper(dataset_name: str) -> DatabaseWrapper:
    """Create a database wrapper for a specific dataset."""
    return DatabaseWrapper(dataset_name)

def get_connection_for_dataset(dataset_name: str) -> mysql.connector.MySQLConnection:
    """Get a raw MySQL connection for a dataset."""
    db_config = get_database_config(dataset_name)
    return mysql.connector.connect(**db_config)

def test_dataset_connection(dataset_name: str) -> bool:
    """Test if we can connect to a dataset's database."""
    try:
        with DatabaseWrapper(dataset_name) as db:
            count = db.get_row_count()
            print(f"[OK] {dataset_name}: Connected successfully, {count} rows in primary table")
            return True
    except Exception as e:
        print(f"[FAIL] {dataset_name}: Connection failed - {e}")
        return False

# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

# For existing code that creates DatabaseConfig with parameters
def create_legacy_database_config(host='localhost', user='root', password='uci@dbh@2084', database='adult'):
    """
    Create DatabaseConfig in the old style for backward compatibility.
    
    This function maps old-style database parameters to dataset names.
    """
    # Try to map database name to dataset name
    database_to_dataset = {
        'adult': 'adult',
        'tax': 'tax',
        'hospital': 'hospital',
        'ncvoter': 'ncvoter',
        'airport': 'airport',
        'RTF25': 'rtf25',
        'tpchdb': 'tpchdb'
    }
    
    dataset_name = database_to_dataset.get(database, 'adult')
    
    # Create config using central configuration
    config = DatabaseConfig(dataset_name)
    
    # Override with provided parameters if they differ from defaults
    central_config = get_database_config(dataset_name)
    if (host != 'localhost' or user != 'root' or 
        password != 'uci@dbh@2084' or database != central_config['database']):
        
        print(f"Warning: Using custom database parameters instead of central config")
        config.config.update({
            'host': host,
            'user': user,
            'password': password,
            'database': database
        })
        # Reconnect with new config
        config.close()
        config.connect()
    
    return config

# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

if __name__ == "__main__":
    print("Enhanced Database Wrapper with Central Configuration")
    print("=" * 60)
    
    # Test available datasets
    datasets = list_available_datasets()
    print(f"\nAvailable datasets: {datasets}")
    
    # Test each dataset connection
    print(f"\nTesting dataset connections:")
    for dataset in datasets:
        test_dataset_connection(dataset)
    
    # Example usage with different datasets
    print(f"\nExample usage:")
    
    # New way (recommended)
    print(f"\n1. Using dataset name (recommended):")
    try:
        with DatabaseWrapper('adult') as db:
            print(f"   Primary table: {db.get_primary_table()}")
            print(f"   Key column: {db.get_key_column()}")
            print(f"   All tables: {db.get_all_tables()}")
            
            # Fetch a sample row
            sample_row = db.fetch_row_by_key(1)
            if sample_row:
                print(f"   Sample row keys: {list(sample_row.keys())}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Backward compatibility
    print(f"\n2. Backward compatibility:")
    try:
        # Old way still works
        db_config = create_legacy_database_config(database='adult')
        db_wrapper = DatabaseWrapper(db_config)
        print(f"   [OK] Legacy DatabaseConfig creation works")
        db_wrapper.close()
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"\nDatabase wrapper ready for gradual migration!")