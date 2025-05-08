from proess_data import target_eid
import mysql.connector
import argparse

class DatabaseConfig:
    """Database configuration and connection management."""
    def __init__(self, host='localhost', user='root', password='uci@dbh@2084', database='RTF25'):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establish database connection with dictionary cursor."""
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

class TableRelationships:
    """Manages table relationships and join conditions."""
    def __init__(self, database):
        self.database = database
        self.primary_keys = self._get_primary_keys()
        self.foreign_keys = self._get_foreign_keys()
        self.valid_tables = self._get_valid_tables()
        self.valid_columns = self._get_valid_columns()

    def _get_valid_tables(self):
        """Get list of valid tables for the database."""
        if self.database == 'RTF25':
            return ['employee', 'payroll', 'tax']
        return ['region', 'nation', 'supplier', 'customer', 'part', 'partsupp', 'orders', 'lineitem']

    def _get_valid_columns(self):
        """Get valid columns for each table in the database."""
        if self.database == 'RTF25':
            return {
                'employee': ['eid', 'name', 'state', 'zip', 'role'],
                'payroll': ['eid', 'salprhr', 'wrkhr', 'dept'],
                'tax': ['eid', 'salary', 'type', 'tax']
            }
        return {
            'region': ['r_regionkey', 'r_name', 'r_comment'],
            'nation': ['n_nationkey', 'n_name', 'n_regionkey', 'n_comment'],
            'supplier': ['s_suppkey', 's_name', 's_address', 's_nationkey', 's_phone', 's_acctbal', 's_comment'],
            'customer': ['c_custkey', 'c_name', 'c_address', 'c_nationkey', 'c_phone', 'c_acctbal', 'c_mktsegment', 'c_comment'],
            'part': ['p_partkey', 'p_name', 'p_mfgr', 'p_brand', 'p_type', 'p_size', 'p_container', 'p_retailprice', 'p_comment'],
            'partsupp': ['ps_partkey', 'ps_suppkey', 'ps_availqty', 'ps_supplycost', 'ps_comment'],
            'orders': ['o_orderkey', 'o_custkey', 'o_orderstatus', 'o_totalprice', 'o_orderdate', 'o_orderpriority', 'o_clerk', 'o_shippriority', 'o_comment'],
            'lineitem': ['l_orderkey', 'l_partkey', 'l_suppkey', 'l_linenumber', 'l_quantity', 'l_extendedprice', 'l_discount', 'l_tax', 'l_returnflag', 'l_linestatus', 'l_shipdate', 'l_commitdate', 'l_receiptdate', 'l_shipinstruct', 'l_shipmode', 'l_comment']
        }

    def validate_table(self, table_name):
        """Validate if a table exists in the database."""
        table_name = table_name.lower()
        if table_name not in self.valid_tables:
            raise ValueError(
                f"Invalid table '{table_name}' for database '{self.database}'. "
                f"Valid tables are: {', '.join(self.valid_tables)}"
            )
        return table_name

    def validate_column(self, table_name, column_name):
        """Validate if a column exists in the table."""
        table_name = self.validate_table(table_name)
        column_name = column_name.lower()
        
        valid_columns = self.valid_columns.get(table_name, [])
        if column_name not in valid_columns:
            raise ValueError(
                f"Invalid column '{column_name}' for table '{table_name}' in database '{self.database}'. "
                f"Valid columns are: {', '.join(valid_columns)}"
            )
        return column_name

    def _get_primary_keys(self):
        """Get primary keys configuration based on database."""
        if self.database == 'RTF25':
            return {
                'employee': ['eid'],
                'payroll': ['eid'],
                'tax': ['eid']
            }
        
        return {
            'region': ['r_regionkey'],
            'nation': ['n_nationkey'],
            'supplier': ['s_suppkey'],
            'customer': ['c_custkey'],
            'part': ['p_partkey'],
            'partsupp': ['ps_partkey', 'ps_suppkey'],
            'orders': ['o_orderkey'],
            'lineitem': ['l_orderkey', 'l_linenumber']
        }

    def _get_foreign_keys(self):
        """Get foreign key relationships based on database."""
        if self.database == 'RTF25':
            return {
                ('employee', 'payroll'): [('eid', 'eid')],
                ('employee', 'tax'): [('eid', 'eid')],
                ('payroll', 'tax'): [('eid', 'eid')]
            }
        
        return {
            ('customer', 'orders'): [('c_custkey', 'o_custkey')],
            ('orders', 'lineitem'): [('o_orderkey', 'l_orderkey')],
            ('lineitem', 'part'): [('l_partkey', 'p_partkey')],
            ('lineitem', 'supplier'): [('l_suppkey', 's_suppkey')],
            ('part', 'partsupp'): [('p_partkey', 'ps_partkey')],
            ('supplier', 'partsupp'): [('s_suppkey', 'ps_suppkey')],
            ('customer', 'nation'): [('c_nationkey', 'n_nationkey')],
            ('supplier', 'nation'): [('s_nationkey', 'n_nationkey')],
            ('nation', 'region'): [('n_regionkey', 'r_regionkey')]
        }

    def get_join_conditions(self, table1, table2):
        """Get join conditions between two tables."""
        table1 = table1.lower()
        table2 = table2.lower()
        
        # Check foreign key relationships
        if (table1, table2) in self.foreign_keys:
            fk_pairs = self.foreign_keys[(table1, table2)]
        elif (table2, table1) in self.foreign_keys:
            fk_pairs = [(col2, col1) for col1, col2 in self.foreign_keys[(table2, table1)]]
        else:
            # Fall back to common primary keys
            keys1 = self.primary_keys.get(table1, [])
            keys2 = self.primary_keys.get(table2, [])
            
            if not keys1 or not keys2:
                raise ValueError(f"Primary keys not defined for tables: {table1} and/or {table2}")
            
            common_keys = set(keys1) & set(keys2)
            if not common_keys:
                raise ValueError(f"No join relationship found between {table1} and {table2}")
            
            fk_pairs = [(key, key) for key in common_keys]
        
        return " AND ".join([f"{table1}.{col1} = {table2}.{col2}" for col1, col2 in fk_pairs])

class DomainInfer:
    """Infers domain bounds for database attributes."""
    def __init__(self, database='RTF25'):
        self.db = DatabaseConfig(database=database)
        self.relationships = TableRelationships(database)

    def get_known_value(self, table_name, known_attr, key_attrs, key_vals):
        """Get value of known_attr using composite key."""
        where_clause = " AND ".join([f"{attr} = %s" for attr in key_attrs])
        query = f"SELECT {known_attr} FROM {table_name} WHERE {where_clause}"
        
        self.db.cursor.execute(query, key_vals)
        row = self.db.cursor.fetchone()
        return row[known_attr] if row else None

    def get_bounds_int_int(self, target_attr, target_table, known_attr, known_table, known_value):
        """Infer bounds for target_attr given known_attr = known_value."""
        assert target_attr != known_attr or target_table != known_table, \
            "Target and known attributes must be different if in same table"
        
        if target_table == known_table:
            return self._get_bounds_same_table(target_attr, target_table, known_attr, known_value)
        return self._get_bounds_cross_table(target_attr, target_table, known_attr, known_table, known_value)

    def _get_bounds_same_table(self, target_attr, table, known_attr, known_value):
        """Get bounds when attributes are in the same table."""
        query_lower = f"""
            SELECT MAX({target_attr}) as max_val 
            FROM {table}
            WHERE {known_attr} < %s
        """
        
        query_upper = f"""
            SELECT MIN({target_attr}) as min_val 
            FROM {table}
            WHERE {known_attr} > %s
        """
        
        self.db.cursor.execute(query_lower, (known_value,))
        pred = self.db.cursor.fetchone()
        lower = pred['max_val'] if pred else float('-inf')

        self.db.cursor.execute(query_upper, (known_value,))
        succ = self.db.cursor.fetchone()
        upper = succ['min_val'] if succ else float('inf')

        return (lower, upper)

    def _get_bounds_cross_table(self, target_attr, target_table, known_attr, known_table, known_value):
        """Get bounds when attributes are in different tables."""
        # Get the key columns that link the tables
        if (target_table, known_table) in self.relationships.foreign_keys:
            keys = [col1 for col1, _ in self.relationships.foreign_keys[(target_table, known_table)]]
        elif (known_table, target_table) in self.relationships.foreign_keys:
            keys = [col2 for _, col2 in self.relationships.foreign_keys[(known_table, target_table)]]
        else:
            # Fall back to common primary keys
            keys1 = self.relationships.primary_keys.get(target_table, [])
            keys2 = self.relationships.primary_keys.get(known_table, [])
            keys = list(set(keys1) & set(keys2))
            if not keys:
                raise ValueError(f"No relationship found between {target_table} and {known_table}")

        # Build the IN clause conditions
        in_conditions = []
        for key in keys:
            in_conditions.append(f"{target_table}.{key} IN (SELECT {known_table}.{key} FROM {known_table} WHERE {known_table}.{known_attr} < %s)")
        
        query_lower = f"""
            SELECT MAX({target_table}.{target_attr}) as max_val
            FROM {target_table}
            WHERE {' AND '.join(in_conditions)}
        """
        
        # Build the IN clause conditions for upper bound
        in_conditions = []
        for key in keys:
            in_conditions.append(f"{target_table}.{key} IN (SELECT {known_table}.{key} FROM {known_table} WHERE {known_table}.{known_attr} > %s)")
        
        query_upper = f"""
            SELECT MIN({target_table}.{target_attr}) as min_val
            FROM {target_table}
            WHERE {' AND '.join(in_conditions)}
        """
        
        self.db.cursor.execute(query_lower, (known_value,) * len(keys))
        pred = self.db.cursor.fetchone()
        lower = pred['max_val'] if pred else float('-inf')

        self.db.cursor.execute(query_upper, (known_value,) * len(keys))
        succ = self.db.cursor.fetchone()
        upper = succ['min_val'] if succ else float('inf')

        return (lower, upper)

    def close(self):
        """Close database connection."""
        self.db.close()

def main():
    """Main function to run the domain inference."""
    parser = argparse.ArgumentParser(
        description='Infer domain bounds for database attributes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using RTF25 database (uses eid as primary key):
  python IGC_d_getBounds.py --db RTF25 --table tax --key-cols eid --key-vals 3 --attr1 salary --attr2 tax

  # Using TPC-H database with default values (orderkey=1, linenumber=1):
  python IGC_d_getBounds.py --db tpchdb

  # Using TPC-H database with different key values:
  python IGC_d_getBounds.py --db tpchdb --key-vals 1 2

  # Using TPC-H database with different attributes:
  python IGC_d_getBounds.py --db tpchdb --attr1 l_quantity --attr2 l_extendedprice --key-vals 1 2
"""
    )
    parser.add_argument('--db', '--database', 
                      default='tpchdb',
                      help='Database name (default: tpchdb)')
    parser.add_argument('--table',
                      help='Table name to process')
    parser.add_argument('--key-cols',
                      nargs='+',
                      help='Key column names')
    parser.add_argument('--key-vals',
                      nargs='+',
                      type=int,
                      help='Key values corresponding to key-cols')
    parser.add_argument('--attr1',
                      help='First attribute to process')
    parser.add_argument('--attr2',
                      help='Second attribute to process')
    
    args = parser.parse_args()
    infer = None

    try:
        infer = DomainInfer(database=args.db)
        
        # Set default values based on database
        if args.db.lower() == 'rtf25':
            if not args.table:
                args.table = 'tax'
            if not args.key_cols:
                args.key_cols = ['eid']
            if not args.key_vals:
                args.key_vals = [3]
            if not args.attr1:
                args.attr1 = 'salary'
            if not args.attr2:
                args.attr2 = 'tax'
        else:  # tpchdb
            if not args.table:
                args.table = 'lineitem'
            if not args.key_cols:
                args.key_cols = ['l_orderkey', 'l_linenumber']
            if not args.key_vals:
                args.key_vals = [1, 1]
            if not args.attr1:
                args.attr1 = 'l_extendedprice'
            if not args.attr2:
                args.attr2 = 'l_discount'

        # Validate table and column names
        args.table = infer.relationships.validate_table(args.table)
        for key_col in args.key_cols:
            infer.relationships.validate_column(args.table, key_col)
        infer.relationships.validate_column(args.table, args.attr1)
        infer.relationships.validate_column(args.table, args.attr2)

        # Process first attribute
        known_value = infer.get_known_value(args.table, args.attr2, args.key_cols, args.key_vals)
        bounds = infer.get_bounds_int_int(args.attr1, args.table, args.attr2, args.table, known_value)
        print(f"\nInferred domain for {args.attr1} when {args.attr2} = {known_value}")
        print(f"Key columns: {args.key_cols}")
        print(f"Key values: {args.key_vals}")
        print(f"Bounds: {bounds}")

        print("\n" + "="*50 + "\n")

        # Process second attribute
        known_value = infer.get_known_value(args.table, args.attr1, args.key_cols, args.key_vals)
        bounds = infer.get_bounds_int_int(args.attr2, args.table, args.attr1, args.table, known_value)
        print(f"Inferred domain for {args.attr2} when {args.attr1} = {known_value}")
        print(f"Key columns: {args.key_cols}")
        print(f"Key values: {args.key_vals}")
        print(f"Bounds: {bounds}")

    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        if infer:
            infer.close()
    
    return 0

if __name__ == "__main__":
    exit(main())

