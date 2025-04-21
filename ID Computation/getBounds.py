from proess_data import target_eid
import mysql.connector

class DomainInferer:
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

    def get_bounds_int_int(self, target_attr, known_attr, known_value, table_name):
        """
        Infer bounds for target_attr given known_attr = known_value based on a DC of the form:
            ¬(t1.A > t2.A ∧ t1.B < t2.B)
        """
        assert target_attr != known_attr, "Target and known attribute must be different"

        # Lower bound
        query_lower = f"""
            SELECT {target_attr} FROM {table_name}
            WHERE {known_attr} < %s
            ORDER BY {known_attr} DESC
            LIMIT 1
        """
        self.cursor.execute(query_lower, (known_value,))
        pred = self.cursor.fetchone()
        lower = pred[target_attr] if pred else float('-inf')

        # Upper bound
        query_upper = f"""
            SELECT {target_attr} FROM {table_name}
            WHERE {known_attr} > %s
            ORDER BY {known_attr} ASC
            LIMIT 1
        """
        self.cursor.execute(query_upper, (known_value,))
        succ = self.cursor.fetchone()
        upper = succ[target_attr] if succ else float('inf')

        return (lower, upper)
    


inferer = DomainInferer()

# Step 1: Get known value for the target row
temp_val = inferer.get_known_value(table_name='Tax', known_attr='Tax', key_attr='EID', key_val=target_eid)

# Step 2: Infer bounds for missing Salary
bounds = inferer.get_bounds_int_int(target_attr='Salary', known_attr='Tax', known_value=temp_val, table_name='Tax')

print(f"Inferred domain for Salary: {bounds}")

inferer.close()

