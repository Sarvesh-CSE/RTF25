"""
Updated Attribute Domain Computation using Central Configuration
==============================================================
Step 2: Replace your current IGC_c_get_global_domain_mysql.py with this version.

This version uses the central config for:
- Database connections (no more hardcoded passwords)
- Dataset information (database names, tables, domain file paths)
- File path management
- Command line interface with dataset validation
"""

import mysql.connector
import json
import os
import argparse
from decimal import Decimal
from typing import Dict, Any, List, Optional
import sys

# Add project root to path for config import
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import from central configuration
from config import (
    get_database_config, get_dataset_info, get_domain_file_path,
    list_available_datasets, validate_dataset, get_all_tables
)

class AttributeDomainComputation:
    """Computes and manages attribute domains using central configuration."""
    
    NUMERIC_TYPES = {'int', 'bigint', 'smallint', 'decimal', 'float', 'double', 'numeric', 'real'}
    STRING_TYPES = {'varchar', 'char', 'text', 'enum', 'set'}
    
    # MySQL reserved keywords that need backticks
    RESERVED_KEYWORDS = {
        'condition', 'order', 'group', 'where', 'select', 'from', 'insert', 
        'update', 'delete', 'create', 'drop', 'alter', 'index', 'key', 'primary',
        'foreign', 'references', 'constraint', 'table', 'database', 'schema',
        'view', 'procedure', 'function', 'trigger', 'event', 'user', 'role'
    }

    def __init__(self, dataset_name: str):
        """
        Initialize domain computation for a specific dataset using central config.
        
        Args:
            dataset_name: Name of the dataset from central configuration
        """
        self.dataset_name = dataset_name
        self.dataset_info = get_dataset_info(dataset_name)
        self.db_config = get_database_config(dataset_name)
        self.domain_file = get_domain_file_path(dataset_name)
        self.domain_map = {}
        
        print(f"Initialized domain computation for dataset: {dataset_name}")
        print(f"Database: {self.dataset_info['database_name']}")
        print(f"Tables: {self.dataset_info['tables']}")
        print(f"Domain file: {self.domain_file}")

    def get_db_connection(self):
        """Get database connection using central configuration."""
        return mysql.connector.connect(**self.db_config)
    
    def escape_column_name(self, column_name: str) -> str:
        """Escape column names that are MySQL reserved keywords."""
        if column_name.lower() in self.RESERVED_KEYWORDS:
            return f"`{column_name}`"
        return column_name

    def convert_decimal_to_float(self, obj: Any) -> Any:
        """Convert Decimal objects to float for JSON serialization."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimal_to_float(item) for item in obj]
        return obj

    def compute_and_save_domains(self, force_recompute: bool = False) -> None:
        """Compute domains for all columns and save to file."""
        if self.domain_file.exists() and not force_recompute:
            print(f"Domain map already exists at {self.domain_file}")
            print("Use --force to recompute or delete the file manually")
            return

        print(f"Computing domains for dataset: {self.dataset_name}")
        print(f"Database: {self.dataset_info['database_name']}")
        print(f"Tables to process: {self.dataset_info['tables']}")
        
        connection = self.get_db_connection()
        cursor = connection.cursor()
        
        # Process each table in the dataset configuration
        for table_name in self.dataset_info['tables']:
            print(f"\nProcessing table: {table_name}")
            
            # Get column information for this specific table
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (self.dataset_info['database_name'], table_name))
            
            columns = cursor.fetchall()
            if not columns:
                print(f"Warning: No columns found for table {table_name}")
                continue
            
            print(f"Found {len(columns)} columns: {[col[0] for col in columns]}")

            for column_name, data_type in columns:
                self._process_column(cursor, table_name, column_name, data_type)

        cursor.close()
        connection.close()

        # Save to file
        self._save_domain_map()

    def _process_column(self, cursor, table_name: str, column_name: str, data_type: str) -> None:
        """Process a single column to compute its domain."""
        data_type = data_type.lower()
        key = (table_name.lower(), column_name.lower())
        escaped_column = self.escape_column_name(column_name)

        try:
            if data_type in self.NUMERIC_TYPES:
                self._process_numeric_column(cursor, table_name, escaped_column, key)
            elif data_type in self.STRING_TYPES:
                self._process_string_column(cursor, table_name, escaped_column, key)
            else:
                print(f"Skipping column {column_name} with unsupported type: {data_type}")
                
        except Exception as e:
            print(f"Error processing column {table_name}.{column_name}: {e}")

    def _process_numeric_column(self, cursor, table_name: str, escaped_column: str, key: tuple) -> None:
        """Process a numeric column."""
        cursor.execute(f"""
            SELECT MIN({escaped_column}), MAX({escaped_column})
            FROM {table_name}
            WHERE {escaped_column} IS NOT NULL
        """)
        min_val, max_val = cursor.fetchone()
        
        # Convert Decimal objects to float for JSON serialization
        min_val = float(min_val) if isinstance(min_val, Decimal) else min_val
        max_val = float(max_val) if isinstance(max_val, Decimal) else max_val
        
        self.domain_map[key] = {
            'type': 'numeric',
            'min': min_val,
            'max': max_val
        }
        print(f"Added numeric domain for {key}: min={min_val}, max={max_val}")

    def _process_string_column(self, cursor, table_name: str, escaped_column: str, key: tuple) -> None:
        """Process a string column."""
        cursor.execute(f"""
            SELECT DISTINCT {escaped_column}
            FROM {table_name}
            WHERE {escaped_column} IS NOT NULL
            ORDER BY {escaped_column}
        """)
        values = [row[0] for row in cursor.fetchall()]
        self.domain_map[key] = {
            'type': 'string',
            'values': values
        }
        print(f"Added string domain for {key} with {len(values)} distinct values")

    def _save_domain_map(self) -> None:
        """Save domain map to JSON file."""
        # Convert any remaining Decimal objects before saving
        serializable_domain_map = self.convert_decimal_to_float(self.domain_map)
        
        # Create the flat mapping for JSON serialization
        flat_domain_map = {f"{k[0]}.{k[1]}": v for k, v in serializable_domain_map.items()}
        
        # Save to file
        with open(self.domain_file, 'w') as f:
            json.dump(flat_domain_map, f, indent=2)
        
        print(f"\nDomain computation completed!")
        print(f"Processed {len(self.domain_map)} columns")
        print(f"Domain map saved to: {self.domain_file}")

    def load_existing_domains(self) -> Dict[str, Any]:
        """Load existing domain map from file."""
        if not self.domain_file.exists():
            return {}
        
        with open(self.domain_file, 'r') as f:
            flat_map = json.load(f)
        
        # Convert flat mapping back to tuple keys
        domain_map = {}
        for key_str, value in flat_map.items():
            table, column = key_str.split('.', 1)
            domain_map[(table, column)] = value
        
        return domain_map

    def get_domain(self, table: str, column: str) -> Optional[Dict[str, Any]]:
        """Get domain for a specific column."""
        if not self.domain_map:
            self.domain_map = self.load_existing_domains()
        
        key = (table.lower(), column.lower())
        return self.domain_map.get(key)

    def print_domain_summary(self) -> None:
        """Print a summary of computed domains."""
        if not self.domain_map:
            self.domain_map = self.load_existing_domains()
        
        print(f"\nDomain Summary for {self.dataset_name}:")
        print("=" * 50)
        
        tables = {}
        for (table, column), domain in self.domain_map.items():
            if table not in tables:
                tables[table] = {'numeric': 0, 'string': 0, 'columns': []}
            
            tables[table][domain['type']] += 1
            tables[table]['columns'].append(column)
        
        for table, info in tables.items():
            print(f"\nTable: {table}")
            print(f"  Columns: {len(info['columns'])}")
            print(f"  Numeric: {info['numeric']}, String: {info['string']}")
            if len(info['columns']) <= 10:
                print(f"  Column names: {info['columns']}")
            else:
                print(f"  Sample columns: {info['columns'][:5]}... (+{len(info['columns'])-5} more)")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description='Compute attribute domains for datasets using central configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python IGC_c_get_global_domain_mysql.py --dataset adult
  python IGC_c_get_global_domain_mysql.py --dataset tax --force
  python IGC_c_get_global_domain_mysql.py --dataset hospital --summary-only
        """
    )
    
    parser.add_argument('--dataset', 
                       choices=list_available_datasets(),
                       required=True,
                       help='Dataset to process')
    
    parser.add_argument('--force', 
                       action='store_true',
                       help='Force recomputation even if domain file exists')
    
    parser.add_argument('--summary-only',
                       action='store_true',
                       help='Only print summary of existing domains')
    
    parser.add_argument('--validate-only',
                       action='store_true',
                       help='Only validate dataset configuration')
    
    args = parser.parse_args()
    
    print("RTF Domain Computation")
    print("=" * 40)
    
    # Validate dataset first
    is_valid, message = validate_dataset(args.dataset)
    if not is_valid:
        print(f"Error: Dataset validation failed: {message}")
        return 1
    
    if args.validate_only:
        print(f"✓ Dataset '{args.dataset}' configuration is valid")
        return 0
    
    try:
        # Initialize domain computation
        adc = AttributeDomainComputation(args.dataset)
        
        if args.summary_only:
            adc.print_domain_summary()
        else:
            adc.compute_and_save_domains(force_recompute=args.force)
            adc.print_domain_summary()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())