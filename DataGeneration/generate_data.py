import pandas as pd
import random
import mysql.connector

class DataGenerator:
    def __init__(self, num_entries=10):
        self.num_entries = num_entries
        self.roles = [1, 2, 3, 4, 5]
        self.depts = ['CS', 'Eng', 'HR', 'Sales']
        self.state_zip_mapping = {
            'NC': [27708, 27514, 27601],
            'CA': [95616, 90001, 94101],
            'NY': [10001, 11201, 12201],
            'TX': [73301, 75001, 77001],
            'FL': [33101, 32801, 33601]
        }
        self.employee_data = []
        self.payroll_data = []
        self.tax_data = []

    def generate_employee_data(self):
        self.employee_data = [
            {
                'EId': i,
                'Name': f'Employee_{i}',
                'State': (state := random.choice(list(self.state_zip_mapping.keys()))),
                'ZIP': random.choice(self.state_zip_mapping[state]),
                'Role': random.choice(self.roles)
            }
            for i in range(1, self.num_entries + 1)
        ]

    def generate_payroll_data(self):
        self.payroll_data = [
            {
                'EId': i,
                'SalPrHr': random.randint(50, 100) if emp['Role'] == 1 else random.randint(100 * emp['Role'], 200 * emp['Role']),
                'WrkHr': random.randint(20, 40),
                'Dept': random.choice(self.depts)
            }
            for i, emp in enumerate(self.employee_data, start=1)
        ]

    def generate_tax_data(self):
        self.tax_data = [
            {
                'EId': emp['EId'],
                'Salary': (salary := emp['SalPrHr'] * emp['WrkHr']),
                'Type': 'Full' if salary >= 5000 else 'Part',
                'Tax': int(salary * 0.2)
            }
            for emp in self.payroll_data
        ]

    def get_db_connection(self):
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='uci@dbh@2084',
            database='RTF25'
        )
    
    def export_to_db(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM Payroll")
        cursor.execute("DELETE FROM Tax")
        cursor.execute("DELETE FROM Employee")

        for emp in self.employee_data:
            cursor.execute("""
                INSERT INTO Employee (EId, Name, State, ZIP, Role)
                VALUES (%s, %s, %s, %s, %s)
            """, (emp['EId'], emp['Name'], emp['State'], emp['ZIP'], emp['Role']))

        for payroll in self.payroll_data:
            cursor.execute("""
                INSERT INTO Payroll (EId, SalPrHr, WrkHr, Dept)
                VALUES (%s, %s, %s, %s)
            """, (payroll['EId'], payroll['SalPrHr'], payroll['WrkHr'], payroll['Dept']))

        for tax in self.tax_data:
            cursor.execute("""
                INSERT INTO Tax (EId, Salary, Type, Tax)
                VALUES (%s, %s, %s, %s)
            """, (tax['EId'], tax['Salary'], tax['Type'], tax['Tax']))

        connection.commit()
        cursor.close()
        connection.close()
    
    def compute_attribute_domain(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()

        db_name = 'RTF25'
        tables = ['Employee', 'Payroll', 'Tax']
        numeric_types = {'int', 'bigint', 'smallint', 'decimal', 'float', 'double', 'numeric', 'real'}

        print("Attribute Domains (Min & Max) per Numerical Column:\n")

        for table in tables:
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (db_name, table))

            columns = cursor.fetchall()
            numeric_columns = [col[0] for col in columns if col[1].lower() in numeric_types]

            for col in numeric_columns:
                cursor.execute(f"""
                    SELECT MIN({col}) AS min_val, MAX({col}) AS max_val
                    FROM {table}
                """)
                result = cursor.fetchone()
                print(f"{table}.{col} -> Min: {result[0]}, Max: {result[1]}")
            print("-" * 50)

        cursor.close()
        connection.close()

    def generate_all(self):
        self.generate_employee_data()
        self.generate_payroll_data()
        self.generate_tax_data()
        self.export_to_db()
        self.compute_attribute_domain()



if __name__ == "__main__":
    generator = DataGenerator(num_entries=10)
    generator.generate_all()


