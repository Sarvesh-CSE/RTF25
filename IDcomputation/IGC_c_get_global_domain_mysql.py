import mysql.connector
import json
import os
import argparse
from decimal import Decimal

class AttributeDomainComputation:
    """Computes and manages attribute domains for database tables."""
    
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'uci@dbh@2084'
    }
    
    NUMERIC_TYPES = {'int', 'bigint', 'smallint', 'decimal', 'float', 'double', 'numeric', 'real'}
    STRING_TYPES = {'varchar', 'char', 'text', 'enum', 'set'}
    
    # MySQL reserved keywords that need backticks
    RESERVED_KEYWORDS = {
        'condition', 'order', 'group', 'where', 'select', 'from', 'insert', 
        'update', 'delete', 'create', 'drop', 'alter', 'index', 'key', 'primary',
        'foreign', 'references', 'constraint', 'table', 'database', 'schema',
        'view', 'procedure', 'function', 'trigger', 'event', 'user', 'role'
    }

    def __init__(self, db_name='RTF25'):
        self.domain_map = {}
        self.db_name = db_name
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.domain_file = os.path.join(self.script_dir, f"{self.db_name}_domain_map.json")

    def get_db_connection(self):
        config = self.DB_CONFIG.copy()
        config['database'] = self.db_name
        return mysql.connector.connect(**config)
    
    def convert_decimal_to_float(self, obj):
        """Convert Decimal objects to float for JSON serialization."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self.convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimal_to_float(item) for item in obj]
        return obj
    def escape_column_name(self, column_name):
        """Escape column names that are MySQL reserved keywords."""
        if column_name.lower() in self.RESERVED_KEYWORDS:
            return f"`{column_name}`"
        return column_name

    def compute_and_save_domains(self):
        """Compute domains for all columns and save to file."""
        if os.path.exists(self.domain_file):
            print(f"Domain map already exists at {self.domain_file}")
            return

        print(f"Computing domains for database: {self.db_name}")
        connection = self.get_db_connection()
        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (self.db_name,))
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found tables: {tables}")

        # Process each table
        for table in tables:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (self.db_name, table))
            
            columns = cursor.fetchall()
            print(f"\nProcessing table {table} with columns: {[col[0] for col in columns]}")

            for column_name, data_type in columns:
                data_type = data_type.lower()
                key = (table.lower(), column_name.lower())
                
                # Escape column name if it's a reserved keyword
                escaped_column = self.escape_column_name(column_name)

                if data_type in self.NUMERIC_TYPES:
                    cursor.execute(f"""
                        SELECT MIN({escaped_column}), MAX({escaped_column})
                        FROM {table}
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

                elif data_type in self.STRING_TYPES:
                    cursor.execute(f"""
                        SELECT DISTINCT {escaped_column}
                        FROM {table}
                        WHERE {escaped_column} IS NOT NULL
                        ORDER BY {escaped_column}
                    """)
                    values = [row[0] for row in cursor.fetchall()]
                    self.domain_map[key] = {
                        'type': 'string',
                        'values': values
                    }
                    print(f"Added string domain for {key} with {len(values)} distinct values")

        cursor.close()
        connection.close()

        # Convert any remaining Decimal objects before saving
        serializable_domain_map = self.convert_decimal_to_float(self.domain_map)
        
        # Save to file
        with open(self.domain_file, 'w') as f:
            json.dump({f"{k[0]}.{k[1]}": v for k, v in serializable_domain_map.items()}, f, indent=2)
        print(f"\nDomain map saved to: {self.domain_file}")

    def get_domain(self, table, column):
        """Get domain for a specific column."""
        if not self.domain_map:
            if not os.path.exists(self.domain_file):
                self.compute_and_save_domains()
            else:
                with open(self.domain_file, 'r') as f:
                    flat_map = json.load(f)
                self.domain_map = {tuple(k.split('.')): v for k, v in flat_map.items()}
        
        key = (table.lower(), column.lower())
        return self.domain_map.get(key)


def main():
    parser = argparse.ArgumentParser(description='Compute attribute domains for a MySQL database')
    parser.add_argument('--db', '--database', 
                      default='RTF25',
                      help='Database name (default: RTF25)')
    parser.add_argument('--table', 
                      help='Specific table to process (optional)')
    parser.add_argument('--column', 
                      help='Specific column to process (optional)')
    
    args = parser.parse_args()
    adc = AttributeDomainComputation(args.db)
    
    if args.table and args.column:
        print(f"\nDomain for {args.table}.{args.column}:")
        print(adc.get_domain(args.table, args.column))
    else:
        adc.compute_and_save_domains()


if __name__ == "__main__":
    main()