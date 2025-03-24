import pandas as pd
import random
import mysql.connector

class DataGenerator:
    def __init__(self, num_entries=10):
        self.num_entries = num_entries
        self.roles = [1, 2, 3, 4, 5]  # Employee roles with increasing seniority
        self.depts = ['CS', 'Eng', 'HR', 'Sales']

        # We are not doing this anymore
        # self.states = ['NC', 'CA', 'NY', 'TX', 'FL']
        # self.zips = [27708, 95616, 10001, 73301, 33101]



        # Define a mapping of states to their respective ZIP codes
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
        """
        Generate basic employee data with random ZIP, State, and Role.
        """
        self.employee_data = [
            {
                'EId': i,
                'Name': f'Employee_{i}',
                'State': (state := random.choice(list(self.state_zip_mapping.keys()))),
                'ZIP': random.choice(self.state_zip_mapping[state]),
                'Role': random.choice(self.roles)  # Role assigned randomly
            }
            for i in range(1, self.num_entries + 1)
        ]

    def generate_payroll_data(self):
        """
        Generate payroll data ensuring:
        - 𝜙₄: If Role == 1, then SalPrHr must be <= 100.
        - For higher roles, SalPrHr is proportionally higher.
        """
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
        """
        Generate tax data ensuring:
        - 𝜙₃: Salary must be calculated as SalPrHr * WrkHr.
        - Tax is computed as 20% of Salary.
        - Employment type is Full if Salary >= 5000, else Part.
        """
        self.tax_data = [
            {
                'EId': emp['EId'],
                'Salary': (salary := emp['SalPrHr'] * emp['WrkHr']),
                'Type': 'Full' if salary >= 5000 else 'Part',
                'Tax': int(salary * 0.2)  # Tax calculated as 20% of salary
            }
            for emp in self.payroll_data
        ]

    def export_to_db(self):
        """
        Export generated data to CSV files and print the first few rows for verification.
        """
        employee_df = pd.DataFrame(self.employee_data)
        payroll_df = pd.DataFrame(self.payroll_data)
        tax_df = pd.DataFrame(self.tax_data)


        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='uci@dbh@2084',
            database='RTF25'
        )
        cursor = connection.cursor()

        # Create tables for employee, payroll, and tax data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Employee (
            EId INT PRIMARY KEY,
            Name VARCHAR(255),
            State VARCHAR(2),
            ZIP INT,
            Role INT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Payroll (
            EId INT PRIMARY KEY,
            SalPrHr INT,
            WrkHr INT,
            Dept VARCHAR(255),
            FOREIGN KEY (EId) REFERENCES Employee(EId)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tax (
            EId INT PRIMARY KEY,
            Salary INT,
            Type VARCHAR(10),
            Tax INT,
            FOREIGN KEY (EId) REFERENCES Employee(EId)
        )
        """)

        # Insert data into the Employee table
        for emp in self.employee_data:
            cursor.execute("""
            INSERT INTO Employee (EId, Name, State, ZIP, Role)
            VALUES (%s, %s, %s, %s, %s)
            """, (emp['EId'], emp['Name'], emp['State'], emp['ZIP'], emp['Role']))

        # Insert data into the Payroll table
        for payroll in self.payroll_data:
            cursor.execute("""
            INSERT INTO Payroll (EId, SalPrHr, WrkHr, Dept)
            VALUES (%s, %s, %s, %s)
            """, (payroll['EId'], payroll['SalPrHr'], payroll['WrkHr'], payroll['Dept']))

        # Insert data into the Tax table
        for tax in self.tax_data:
            cursor.execute("""
            INSERT INTO Tax (EId, Salary, Type, Tax)
            VALUES (%s, %s, %s, %s)
            """, (tax['EId'], tax['Salary'], tax['Type'], tax['Tax']))

        # Commit the transaction and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        print("Employee Table:\n", employee_df.head())
        print("\nPayroll Table:\n", payroll_df.head())
        print("\nTax Table:\n", tax_df.head())

    def generate_all(self):
        """
        Sequentially generate all datasets and ensure constraints are followed.
        - 𝜙₁: Higher tax should not correspond to lower salary.
        - 𝜙₂: Higher roles must have higher or equal SalPrHr.
        """
        self.generate_employee_data()
        self.generate_payroll_data()
        self.generate_tax_data()
        self.export_to_db()

# Generate and export the data
if __name__ == "__main__":
    generator = DataGenerator(num_entries=10)
    generator.generate_all()