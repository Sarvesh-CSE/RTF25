from proess_data import target_eid
import mysql.connector



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

    def get_bounds_int_int(self, target_attr, target_table, known_attr, known_table, known_value, join_key=None):
        """
        Infer bounds for target_attr given known_attr = known_value based on a DC of the form:
            ¬(t1.A > t2.A ∧ t1.B < t2.B)
        
        This method handles both cases:
        1. When target_attr and known_attr are from the same table (join_key not needed)
        2. When they are from different tables (requires join_key)
        
        Parameters:
        - target_attr: The attribute we want to find bounds for
        - target_table: The table containing target_attr
        - known_attr: The attribute with known value
        - known_table: The table containing known_attr
        - known_value: The value of known_attr
        - join_key: The key used to join tables if different (e.g., 'EID'). Optional if same table.
        """
        # Validate inputs
        assert target_attr != known_attr or target_table != known_table, "Target and known attributes must be different if in same table"
        
        # Determine if we're working with same or different tables
        same_table = (target_table == known_table)
        
        if same_table:
            # Lower bound - same table case
            query_lower = f"""
                SELECT {target_attr} FROM {target_table}
                WHERE {known_attr} < %s
                ORDER BY {known_attr} DESC
                LIMIT 1
            """
            # Upper bound - same table case
            query_upper = f"""
                SELECT {target_attr} FROM {target_table}
                WHERE {known_attr} > %s
                ORDER BY {known_attr} ASC
                LIMIT 1
            """
        else:
            # Validate join_key for cross-table case
            if not join_key:
                raise ValueError("join_key is required when target_table and known_table are different")
                
            # Lower bound - cross table case
            query_lower = f"""
                SELECT t1.{target_attr} 
                FROM {target_table} t1
                JOIN {known_table} t2 ON t1.{join_key} = t2.{join_key}
                WHERE t2.{known_attr} < %s
                ORDER BY t2.{known_attr} DESC
                LIMIT 1
            """
            # Upper bound - cross table case
            query_upper = f"""
                SELECT t1.{target_attr}
                FROM {target_table} t1
                JOIN {known_table} t2 ON t1.{join_key} = t2.{join_key}
                WHERE t2.{known_attr} > %s
                ORDER BY t2.{known_attr} ASC
                LIMIT 1
            """

        # Execute queries and get bounds
        self.cursor.execute(query_lower, (known_value,))
        pred = self.cursor.fetchone()
        lower = pred[target_attr] if pred else float('-inf')

        self.cursor.execute(query_upper, (known_value,))
        succ = self.cursor.fetchone()
        upper = succ[target_attr] if succ else float('inf')

        return (lower, upper)
    


infer = DomainInfer()

# Step 1: Get known value for the target row
temp_val = infer.get_known_value(table_name='Tax', known_attr='Tax', key_attr='EID', key_val=target_eid)

# Step 2: Infer bounds for missing Salary
bounds = infer.get_bounds_int_int(target_attr='Salary', target_table='Tax', known_attr='Tax', known_table='Tax', known_value=temp_val)

print(f"Inferred domain for Salary: {bounds}")


print("=====================================")


# Step 1: Get known value for the target row
temp_val = infer.get_known_value(table_name='Tax', known_attr='Salary', key_attr='EID', key_val=target_eid)

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

