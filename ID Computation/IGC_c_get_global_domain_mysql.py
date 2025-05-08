import mysql.connector
import json
import os
import argparse

class AttributeDomainComputation:
    """
    Computes and manages attribute domains for database tables.
    Supports both numeric and string domains, with automatic persistence to JSON.
    """
    
    # Database connection settings
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'uci@dbh@2084'
    }
    
    # SQL data types for domain computation
    NUMERIC_TYPES = {'int', 'bigint', 'smallint', 'decimal', 'float', 'double', 'numeric', 'real'}
    STRING_TYPES = {'varchar', 'char', 'text', 'enum', 'set'}

    def __init__(self, db_name='RTF25'):
        """Initialize the domain computation with database name."""
        self.domain_map = {}
        self.db_name = db_name
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def get_db_connection(self):
        """Create and return a database connection."""
        config = self.DB_CONFIG.copy()
        config['database'] = self.db_name
        return mysql.connector.connect(**config)

    def compute_attribute_domain(self):
        """
        Compute domains for all attributes in all tables.
        For numeric types: computes min/max
        For string types: collects distinct values
        """
        connection = self.get_db_connection()
        cursor = connection.cursor()
        
        # Get all tables
        tables = self._get_all_tables(cursor)
        print(f"Found tables in {self.db_name}: {tables}")
        
        # Clear existing domain map
        self.domain_map = {}

        # Process each table
        for table in tables:
            self._process_table(cursor, table)

        cursor.close()
        connection.close()
        print("Attribute domain computation completed.")
        print("Domain map populated with keys:", sorted(self.domain_map.keys()))

    def _get_all_tables(self, cursor):
        """Get list of all tables in the database."""
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (self.db_name,))
        return [row[0] for row in cursor.fetchall()]

    def _process_table(self, cursor, table):
        """Process all columns in a given table."""
        # Get column information
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (self.db_name, table))
        
        columns = cursor.fetchall()
        print(f"Processing table {table} with columns: {[col[0] for col in columns]}")

        # Process each column
        for column_name, data_type in columns:
            self._process_column(cursor, table, column_name, data_type.lower())

    def _process_column(self, cursor, table, column_name, data_type):
        """Process a single column and add its domain to the map."""
        # Store keys in lowercase for consistency
        key = (table.lower(), column_name.lower())

        if data_type in self.NUMERIC_TYPES:
            self._process_numeric_column(cursor, table, column_name, key)
        elif data_type in self.STRING_TYPES:
            self._process_string_column(cursor, table, column_name, key)

    def _process_numeric_column(self, cursor, table, column_name, key):
        """Process a numeric column and compute its min/max values."""
        cursor.execute(f"""
            SELECT MIN({column_name}), MAX({column_name})
            FROM {table}
        """)
        min_val, max_val = cursor.fetchone()
        self.domain_map[key] = {
            'type': 'numeric',
            'min': min_val,
            'max': max_val
        }
        print(f"Added numeric domain for {key}: min={min_val}, max={max_val}")

    def _process_string_column(self, cursor, table, column_name, key):
        """Process a string column and collect its distinct values."""
        cursor.execute(f"""
            SELECT DISTINCT {column_name}
            FROM {table}
            WHERE {column_name} IS NOT NULL
            ORDER BY {column_name}
        """)
        values = [row[0] for row in cursor.fetchall()]
        self.domain_map[key] = {
            'type': 'string',
            'values': values
        }
        print(f"Added string domain for {key} with {len(values)} distinct values")

    def save_domain_map(self, filepath=None):
        """Save the domain map to a JSON file."""
        if filepath is None:
            filepath = os.path.join(self.script_dir, f"{self.db_name}_domain_map.json")
        
        # Convert tuple keys to string format for JSON serialization
        json_data = {f"{k[0]}.{k[1]}": v for k, v in self.domain_map.items()}
        
        with open(filepath, 'w') as f:
            json.dump(json_data, f, indent=2)
        print("Saving to:", filepath)

    def load_domain_map(self, filepath=None):
        """Load the domain map from a JSON file."""
        if filepath is None:
            filepath = os.path.join(self.script_dir, f"{self.db_name}_domain_map.json")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No domain map found at {filepath}")

        try:
            with open(filepath, 'r') as f:
                flat_map = json.load(f)
            self.domain_map = {tuple(k.split('.')): v for k, v in flat_map.items()}
            print(f"Domain map loaded from {filepath}")
        except json.JSONDecodeError as e:
            print(f"Error reading {filepath}: {e}. Recomputing domain map...")
            self.compute_attribute_domain()
            self.save_domain_map(filepath)

    def get_domain(self, table, column, domain_file=None):
        """
        Get the domain for a specific table and column.
        Will compute and save if not found.
        """
        # Convert to lowercase for case-insensitive comparison
        table_lower = table.lower()
        column_lower = column.lower()
        key = (table_lower, column_lower)
        
        print(f"Looking up domain for table: {table_lower}, column: {column_lower}")

        # Load domain map if empty
        if not self.domain_map:
            try:
                self.load_domain_map(domain_file)
            except FileNotFoundError:
                print("Domain map file not found. Computing domain map...")
                self.compute_attribute_domain()
                self.save_domain_map(domain_file)

        # Recompute if key not found
        if key not in self.domain_map:
            print(f"Domain for {key} not found. Recomputing full domain map...")
            self.compute_attribute_domain()
            self.save_domain_map(domain_file)
            
            if key not in self.domain_map:
                print(f"Warning: Domain still not found for {key} after recomputing")
                return None

        return self.domain_map.get(key)


def main():
    """Main function to handle command line arguments and run domain computation."""
    parser = argparse.ArgumentParser(description='Compute attribute domains for a MySQL database')
    parser.add_argument('--db', '--database', 
                      default='RTF25',
                      help='Database name (default: RTF25)')
    parser.add_argument('--table', 
                      help='Specific table to process (optional)')
    parser.add_argument('--column', 
                      help='Specific column to process (optional)')
    
    args = parser.parse_args()
    
    # Initialize domain computation
    adc = AttributeDomainComputation(args.db)
    
    if args.table and args.column:
        # Process specific table and column
        print(f"\nAccessing Domain for {args.table}.{args.column}:")
        print(adc.get_domain(args.table, args.column))
    else:
        # Process all tables and columns
        print("\nAccessing Domains:")
        print("lineitem.l_linenumber:", adc.get_domain("lineitem", "l_linenumber"))


if __name__ == "__main__":
    main()
