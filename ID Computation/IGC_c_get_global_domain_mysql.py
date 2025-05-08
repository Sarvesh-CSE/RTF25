import mysql.connector
import json
import os
import argparse

class AttributeDomainComputation:
    """Computes and manages attribute domains for database tables."""
    
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'uci@dbh@2084'
    }
    
    NUMERIC_TYPES = {'int', 'bigint', 'smallint', 'decimal', 'float', 'double', 'numeric', 'real'}
    STRING_TYPES = {'varchar', 'char', 'text', 'enum', 'set'}

    def __init__(self, db_name='RTF25'):
        self.domain_map = {}
        self.db_name = db_name
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.domain_file = os.path.join(self.script_dir, f"{self.db_name}_domain_map.json")

    def get_db_connection(self):
        config = self.DB_CONFIG.copy()
        config['database'] = self.db_name
        return mysql.connector.connect(**config)

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

                if data_type in self.NUMERIC_TYPES:
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

                elif data_type in self.STRING_TYPES:
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

        # Save to file
        with open(self.domain_file, 'w') as f:
            json.dump({f"{k[0]}.{k[1]}": v for k, v in self.domain_map.items()}, f, indent=2)
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
