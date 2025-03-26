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

        # Delete all existing rows in the dependent tables first
        cursor.execute("DELETE FROM Payroll")
        cursor.execute("DELETE FROM Tax")

        # Delete all existing rows in the Employee table
        cursor.execute("DELETE FROM Employee")

        # Insert data into the Employee table
        for emp in self.employee_data:

            # Insert data into the Employee table
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
        # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='uci@dbh@2084',
            database='RTF25'
        )
    cursor = connection.cursor()


    delset = {"Salary", "Tax", "Role", "WrkHr"}
    target_eid = 2
    # Update the Salary of EID 2 to NULL in the Tax table
    if "Salary" in delset:
        cursor.execute("UPDATE Tax SET Salary = NULL WHERE EID = %s", (target_eid,))
        connection.commit()
        print(f"Salary for EID {target_eid} has been set to NULL.")

    # Fetch the state of Employee, Payroll, and Tax tables
    # Fetch only the rows associated with EID 2 across the database
    database_state = {
        "Employee": {
            "EID": [row[0] for row in cursor.execute("SELECT EID FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "Name": [row[0] for row in cursor.execute("SELECT Name FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "State": [row[0] for row in cursor.execute("SELECT State FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "ZIP": [row[0] for row in cursor.execute("SELECT ZIP FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "Role": [row[0] for row in cursor.execute("SELECT Role FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()]
        },
        "Payroll": {
            "EID": [row[0] for row in cursor.execute("SELECT EID FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "SalPrHr": [row[0] for row in cursor.execute("SELECT SalPrHr FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "WrkHr": [row[0] for row in cursor.execute("SELECT WrkHr FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "Dept": [row[0] for row in cursor.execute("SELECT Dept FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()]
        },
        "Tax": {
            "EID": [row[0] for row in cursor.execute("SELECT EID FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "Salary": [row[0] for row in cursor.execute("SELECT Salary FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "Type": [row[0] for row in cursor.execute("SELECT Type FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
            "Tax": [row[0] for row in cursor.execute("SELECT Tax FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()]
        }
    }
    print("Pulled in Database State w.r.t. target cell C:")
    for table, columns in database_state.items():
        print(f"{table}:")
        for col, data in columns.items():
            print(f"{col}: {data}")



    # Step 1: Filter the columns in the `delset` and fetch only relevant columns for each table from the database state
    # We can incorporate this logic while pulling the data from the database itself by restricting the columns. However, we are doing it here for demonstration purposes.
    filtered_data = {}
    for table_name, table_data in database_state.items():
        filtered_data[table_name] = {
            col: table_data[col]
            for col in table_data.keys() if col in delset
        }
    print("Filtered Data:")
    for table, columns in filtered_data.items():
        print(f"{table}:")
        for col, data in columns.items():
            print(f"{col}: {data}")
    # At this point, we have only those cells and their values that are part of the `delset` for a given target cell C.

    # Mark the target cell explicitly in the filtered data
    target_cell = {"Tax.Salary": None}  # The cell set to NULL in line 213-214
    filtered_data["Tax"]["Salary"] = [None]  # Reflect the NULL value in the filtered data

    
    # Step 2: Generate the inference graph
    inference_graph = {}
    for table_name, columns in filtered_data.items():
        for col, values in columns.items():
            inference_graph[f"{table_name}.{col}"] = values

    # Step 3: Identify the target `delset` for a specific target cell
    target_delset = {
        key: values for key, values in inference_graph.items() if key.split(".")[1] in delset
    }

    # Step 4: Compute dependencies and relationships
    dependencies = {}
    for key, values in target_delset.items():
        table, column = key.split(".")
        dependencies[key] = {
            "table": table,
            "column": column,
            "related_values": values
        }

    # Print the dependencies for verification
    print("Dependencies and Relationships:")
    for key, dep in dependencies.items():
        print(f"{key}: {dep}")

    no_auto_delset = {
        attr for table in database_state.values() for attr in table.keys()
    } - delset
    print("Non-deletable columns are:", no_auto_delset)

    # Close the database connection
    connection.close()

