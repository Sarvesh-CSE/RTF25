from proess_data import target_eid
import mysql.connector
import argparse



class DomainInfer:
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
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def get_known_value(self, table_name, known_attr, key_attr, key_val):
        """
        Get the value of known_attr from table_name where key_attr = key_val.
        E.g., get Tax where EID = 2
        """
        query = f"SELECT {known_attr} FROM {table_name} WHERE {key_attr} = %s"
        self.cursor.execute(query, (key_val,))
        row = self.cursor.fetchone()
        return row[known_attr] if row else None

    def get_bounds_int_int(self, target_attr, target_table, known_attr, known_table, known_value):
        """
        Infer bounds for target_attr given known_attr = known_value based on a DC of the form:
            ¬(t1.A > t2.A ∧ t1.B < t2.B)
        
        This method handles both same-table and cross-table cases without using joins.
        
        Parameters:
        - target_attr: The attribute we want to find bounds for
        - target_table: The table containing target_attr
        - known_attr: The attribute with known value
        - known_table: The table containing known_attr
        - known_value: The value of known_attr
        """
        # Validate inputs
        assert target_attr != known_attr or target_table != known_table, "Target and known attributes must be different if in same table"
        
        if target_table == known_table:
            # Same table case - use direct queries
            query_lower = f"""
                SELECT MAX({target_attr}) as max_val FROM {target_table}
                WHERE {known_attr} < %s
            """
            query_upper = f"""
                SELECT MIN({target_attr}) as min_val FROM {target_table}
                WHERE {known_attr} > %s
            """
            params = (known_value,)
        else:
            # Cross-table case - first get EIDs, then find bounds
            # Get EIDs from known table where known_attr < known_value
            query_get_eids_lower = f"""
                SELECT EID FROM {known_table}
                WHERE {known_attr} < %s
                ORDER BY {known_attr} DESC
                LIMIT 1
            """
            # Get EIDs from known table where known_attr > known_value
            query_get_eids_upper = f"""
                SELECT EID FROM {known_table}
                WHERE {known_attr} > %s
                ORDER BY {known_attr} ASC
                LIMIT 1
            """
            
            # Execute to get EIDs
            self.cursor.execute(query_get_eids_lower, (known_value,))
            eid_lower = self.cursor.fetchone()
            
            self.cursor.execute(query_get_eids_upper, (known_value,))
            eid_upper = self.cursor.fetchone()
            
            # Now get bounds using the EIDs
            query_lower = f"""
                SELECT {target_attr} FROM {target_table}
                WHERE EID = %s
            """
            query_upper = f"""
                SELECT {target_attr} FROM {target_table}
                WHERE EID = %s
            """
            params = (eid_lower['EID'] if eid_lower else None, eid_upper['EID'] if eid_upper else None)

        # Execute queries and get bounds
        if target_table == known_table:
            self.cursor.execute(query_lower, params)
            pred = self.cursor.fetchone()
            lower = pred['max_val'] if pred else float('-inf')

            self.cursor.execute(query_upper, params)
            succ = self.cursor.fetchone()
            upper = succ['min_val'] if succ else float('inf')
        else:
            # For cross-table case, we need to handle the EID queries
            lower = float('-inf')
            if params[0] is not None:
                self.cursor.execute(query_lower, (params[0],))
                pred = self.cursor.fetchone()
                if pred:
                    lower = pred[target_attr]

            upper = float('inf')
            if params[1] is not None:
                self.cursor.execute(query_upper, (params[1],))
                succ = self.cursor.fetchone()
                if succ:
                    upper = succ[target_attr]

        return (lower, upper)
    


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Infer domain bounds for database attributes')
    parser.add_argument('--db', '--database', 
                      default='RTF25',
                      help='Database name (default: RTF25)')
    parser.add_argument('--eid',
                      type=int,
                      default=target_eid,
                      help=f'Target EID to process (default: {target_eid})')
    
    args = parser.parse_args()
    
    # Initialize with database name from command line
    infer = DomainInfer(database=args.db)

    # Step 1: Get known value for the target row
    temp_val = infer.get_known_value(table_name='Tax', known_attr='Tax', key_attr='EID', key_val=args.eid)

    # temp_val = infer.get_known_value(table_name='tpchdb.lineitem', known_attr='l_discount', key_attr='l_orderkey', key_val=1)
    # print(temp_val)

    # Step 2: Infer bounds for missing Salary
    bounds = infer.get_bounds_int_int(target_attr='Salary', target_table='Tax', known_attr='Tax', known_table='Tax', known_value=temp_val)

    print(f"Inferred domain for Salary: {bounds}")

    print("=====================================")

    # Step 1: Get known value for the target row
    temp_val = infer.get_known_value(table_name='Tax', known_attr='Salary', key_attr='EID', key_val=args.eid)

    # Step 2: Infer bounds for missing Tax
    bounds = infer.get_bounds_int_int(target_attr='Tax', target_table='Tax', known_attr='Salary', known_table='Tax', known_value=temp_val)

    print(f"Inferred domain for Tax: {bounds}")

    print("=====================================")

    # Step 1: Get known value for the target row
    temp_val = infer.get_known_value(table_name='Tax', known_attr='Salary', key_attr='EID', key_val=3)

    # Step 2: Infer bounds for missing Tax
    bounds = infer.get_bounds_int_int(target_attr='Tax', target_table='Tax', known_attr='Salary', known_table='Tax', known_value=temp_val)

    print(f"Inferred domain for Tax: {bounds}")

    infer.close()

