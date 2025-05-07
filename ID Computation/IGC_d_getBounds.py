from proess_data import target_eid
import mysql.connector
import argparse



class DomainInfer:
    """
    A class to infer domain bounds for attributes in a database.
    Uses a dependency constraint of the form: ¬(t1.A > t2.A ∧ t1.B < t2.B)
    to find bounds for one attribute given a value of another attribute.
    """
    def __init__(self, host='localhost', user='root', password='uci@dbh@2084', database='RTF25'):
        """Initialize database connection parameters."""
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

    def get_known_value(self, table_name, known_attr, key_attrs, key_vals):
        """
        Get the value of known_attr from table_name using composite key.
        
        Parameters:
        - table_name: Name of the table
        - known_attr: Attribute to get value for
        - key_attrs: List of key column names
        - key_vals: List of key values corresponding to key_attrs
        
        Returns:
        - The value of known_attr or None if not found
        """
        # Build WHERE clause for all key columns
        where_clause = " AND ".join([f"{attr} = %s" for attr in key_attrs])
        query = f"SELECT {known_attr} FROM {table_name} WHERE {where_clause}"
        
        # Execute query and return result
        self.cursor.execute(query, key_vals)
        row = self.cursor.fetchone()
        return row[known_attr] if row else None

    def get_bounds_int_int(self, target_attr, target_table, known_attr, known_table, known_value):
        """
        Infer bounds for target_attr given known_attr = known_value.
        
        The method uses a dependency constraint of the form:
        ¬(t1.A > t2.A ∧ t1.B < t2.B)
        
        This means if we know a value for attribute B, we can find bounds for attribute A:
        - Lower bound: MAX of A where B < known_value
        - Upper bound: MIN of A where B > known_value
        
        Parameters:
        - target_attr: The attribute we want to find bounds for
        - target_table: The table containing target_attr
        - known_attr: The attribute with known value
        - known_table: The table containing known_attr
        - known_value: The value of known_attr
        
        Returns:
        - tuple: (lower_bound, upper_bound) where bounds can be float('-inf') or float('inf')
        """
        # Validate inputs
        assert target_attr != known_attr or target_table != known_table, \
            "Target and known attributes must be different if in same table"
        
        # Use appropriate method based on whether attributes are in same table
        if target_table == known_table:
            return self._get_bounds_same_table(target_attr, target_table, known_attr, known_value)
        else:
            return self._get_bounds_cross_table(target_attr, target_table, known_attr, known_table, known_value)

    def _get_bounds_same_table(self, target_attr, table, known_attr, known_value):
        """
        Get bounds when target and known attributes are in the same table.
        Uses direct MIN/MAX queries for efficiency.
        """
        # Get lower bound: MAX of target_attr where known_attr < known_value
        query_lower = f"""
            SELECT MAX({target_attr}) as max_val 
            FROM {table}
            WHERE {known_attr} < %s
        """
        
        # Get upper bound: MIN of target_attr where known_attr > known_value
        query_upper = f"""
            SELECT MIN({target_attr}) as min_val 
            FROM {table}
            WHERE {known_attr} > %s
        """
        
        # Execute queries and get bounds
        self.cursor.execute(query_lower, (known_value,))
        pred = self.cursor.fetchone()
        lower = pred['max_val'] if pred else float('-inf')

        self.cursor.execute(query_upper, (known_value,))
        succ = self.cursor.fetchone()
        upper = succ['min_val'] if succ else float('inf')

        return (lower, upper)

    def _get_bounds_cross_table(self, target_attr, target_table, known_attr, known_table, known_value):
        """
        Get bounds when target and known attributes are in different tables.
        Uses EXISTS subqueries to maintain relationships between tables.
        """
        # Get lower bound: MAX of target_attr where known_attr < known_value
        query_lower = f"""
            SELECT MAX(t1.{target_attr}) as max_val
            FROM {target_table} t1
            WHERE EXISTS (
                SELECT 1 
                FROM {known_table} t2 
                WHERE t2.{known_attr} < %s
                AND t1.EID = t2.EID
            )
        """
        
        # Get upper bound: MIN of target_attr where known_attr > known_value
        query_upper = f"""
            SELECT MIN(t1.{target_attr}) as min_val
            FROM {target_table} t1
            WHERE EXISTS (
                SELECT 1 
                FROM {known_table} t2 
                WHERE t2.{known_attr} > %s
                AND t1.EID = t2.EID
            )
        """
        
        # Execute queries and get bounds
        self.cursor.execute(query_lower, (known_value,))
        pred = self.cursor.fetchone()
        lower = pred['max_val'] if pred else float('-inf')

        self.cursor.execute(query_upper, (known_value,))
        succ = self.cursor.fetchone()
        upper = succ['min_val'] if succ else float('inf')

        return (lower, upper)


if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description='Infer domain bounds for database attributes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using default values (orderkey=1, linenumber=1):
  python IGC_d_getBounds.py

  # Using different key values (orderkey=1, linenumber=2):
  python IGC_d_getBounds.py --key-vals 1 2

  # Using different attributes and key values:
  python IGC_d_getBounds.py --attr1 l_quantity --attr2 l_extendedprice --key-vals 1 2
"""
    )
    parser.add_argument('--db', '--database', 
                      default='tpchdb',
                      help='Database name (default: tpchdb)')
    parser.add_argument('--table',
                      default='lineitem',
                      help='Table name to process (default: lineitem)')
    parser.add_argument('--key-cols',
                      nargs='+',
                      default=['l_orderkey', 'l_linenumber'],
                      help='Key column names (default: l_orderkey l_linenumber)')
    parser.add_argument('--key-vals',
                      nargs='+',
                      type=int,
                      default=[1, 1],
                      help='Key values corresponding to key-cols (default: 1 1). Example: --key-vals 1 2 means orderkey=1, linenumber=2')
    parser.add_argument('--attr1',
                      default='l_extendedprice',
                      help='First attribute to process (default: l_extendedprice)')
    parser.add_argument('--attr2',
                      default='l_discount',
                      help='Second attribute to process (default: l_discount)')
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Initialize domain inference with database name
    infer = DomainInfer(database=args.db)

    # Step 1: Get known value for the target row
    known_value = infer.get_known_value(table_name=args.table, 
                                      known_attr=args.attr2, 
                                      key_attrs=args.key_cols,
                                      key_vals=args.key_vals)

    # Step 2: Infer bounds for first attribute
    bounds = infer.get_bounds_int_int(target_attr=args.attr1, 
                                    target_table=args.table, 
                                    known_attr=args.attr2, 
                                    known_table=args.table, 
                                    known_value=known_value)

    # Print results for first attribute
    print(f"\nInferred domain for {args.attr1} when {args.attr2} = {known_value}")
    print(f"Key columns: {args.key_cols}")
    print(f"Key values: {args.key_vals}")
    print(f"Bounds: {bounds}")

    print("\n" + "="*50 + "\n")

    # Step 3: Get known value for the target row (other attribute)
    known_value = infer.get_known_value(table_name=args.table, 
                                      known_attr=args.attr1, 
                                      key_attrs=args.key_cols,
                                      key_vals=args.key_vals)

    # Step 4: Infer bounds for second attribute
    bounds = infer.get_bounds_int_int(target_attr=args.attr2, 
                                    target_table=args.table, 
                                    known_attr=args.attr1, 
                                    known_table=args.table, 
                                    known_value=known_value)

    # Print results for second attribute
    print(f"Inferred domain for {args.attr2} when {args.attr1} = {known_value}")
    print(f"Key columns: {args.key_cols}")
    print(f"Key values: {args.key_vals}")
    print(f"Bounds: {bounds}")

    # Clean up
    infer.close()

