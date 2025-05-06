import mysql.connector
import json
import os
import argparse

class AttributeDomainComputation:
    def __init__(self, db_name='RTF25'):
        self.domain_map = {}
        self.db_name = db_name
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def get_db_connection(self):
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='uci@dbh@2084',
            database=self.db_name
        )

    def compute_attribute_domain(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()
        
        # Get all tables from the database
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (self.db_name,))
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found tables in {self.db_name}: {tables}")
        
        numeric_types = {'int', 'bigint', 'smallint', 'decimal', 'float', 'double', 'numeric', 'real'}
        string_types = {'varchar', 'char', 'text', 'enum', 'set'}

        # Clear existing domain map
        self.domain_map = {}

        for table in tables:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (self.db_name, table))
            
            columns = cursor.fetchall()
            print(f"Processing table {table} with columns: {[col[0] for col in columns]}")

            for column_name, data_type in columns:
                data_type = data_type.lower()
                # Always store keys in lowercase
                key = (table.lower(), column_name.lower())

                if data_type in numeric_types:
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

                elif data_type in string_types:
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

        cursor.close()
        connection.close()
        print("Attribute domain computation completed.") 
        print("Domain map populated with keys:", sorted(self.domain_map.keys()))

    def save_domain_map(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(self.script_dir, f"{self.db_name}_domain_map.json")
        with open(filepath, 'w') as f:
            json.dump({f"{k[0]}.{k[1]}": v for k, v in self.domain_map.items()}, f, indent=2)
        print("Saving to:", filepath)

    def load_domain_map(self, filepath=None):
        if filepath is None:
            filepath = os.path.join(self.script_dir, f"{self.db_name}_domain_map.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    flat_map = json.load(f)
                self.domain_map = {tuple(k.split('.')): v for k, v in flat_map.items()}
                print(f"Domain map loaded from {filepath}")
            except json.JSONDecodeError as e:
                print(f"Error reading {filepath}: {e}. Recomputing domain map...")
                self.compute_attribute_domain()
                self.save_domain_map(filepath)
        else:
            raise FileNotFoundError(f"No domain map found at {filepath}")

    def get_domain(self, table, column, domain_file=None):
        # Convert table and column names to lowercase for case-insensitive comparison
        table_lower = table.lower()
        column_lower = column.lower()
        key = (table_lower, column_lower)
        
        print(f"Looking up domain for table: {table_lower}, column: {column_lower}")

        # Load if domain_map is empty
        if not self.domain_map:
            try:
                self.load_domain_map(domain_file)
            except FileNotFoundError:
                print(f"Domain map file not found. Computing domain map...")
                self.compute_attribute_domain()
                self.save_domain_map(domain_file)

        # If key still not found, recompute and save
        if key not in self.domain_map:
            print(f"Domain for {key} not found. Recomputing full domain map...")
            self.compute_attribute_domain()
            self.save_domain_map(domain_file)
            # Check if the key exists after recomputing
            if key not in self.domain_map:
                print(f"Warning: Domain still not found for {key} after recomputing")
                return None

        return self.domain_map.get(key)

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Compute attribute domains for a MySQL database')
    parser.add_argument('--db', '--database', 
                      default='RTF25',
                      help='Database name (default: RTF25)')
    parser.add_argument('--table', 
                      help='Specific table to process (optional)')
    parser.add_argument('--column', 
                      help='Specific column to process (optional)')
    
    args = parser.parse_args()
    
    # Initialize with database name from command line
    adc = AttributeDomainComputation(args.db)
    
    if args.table and args.column:
        # Process specific table and column
        print(f"\nAccessing Domain for {args.table}.{args.column}:")
        print(adc.get_domain(args.table, args.column))
    else:
        # Process all tables and columns
        print("\nAccessing Domains:")
        print("lineitem.l_linenumber:", adc.get_domain("lineitem", "l_linenumber"))
        # print("Employee.State:", adc.get_domain("line_item", "State"))
