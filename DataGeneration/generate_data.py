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

    def export_to_db(self):
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='uci@dbh@2084',
            database='RTF25'
        )
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

    def generate_all(self):
        self.generate_employee_data()
        self.generate_payroll_data()
        self.generate_tax_data()
        self.export_to_db()


# def fetch_database_state(target_eid, delset):
#     connection = mysql.connector.connect(
#         host='localhost',
#         user='root',
#         password='uci@dbh@2084',
#         database='RTF25'
#     )
#     cursor = connection.cursor()

#     database_state = {
#         "Employee": {
#             "EID": [row[0] for row in cursor.execute("SELECT EID FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "Name": [row[0] for row in cursor.execute("SELECT Name FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "State": [row[0] for row in cursor.execute("SELECT State FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "ZIP": [row[0] for row in cursor.execute("SELECT ZIP FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "Role": [row[0] for row in cursor.execute("SELECT Role FROM Employee WHERE EID = %s", (target_eid,)) or cursor.fetchall()]
#         },
#         "Payroll": {
#             "EID": [row[0] for row in cursor.execute("SELECT EID FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "SalPrHr": [row[0] for row in cursor.execute("SELECT SalPrHr FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "WrkHr": [row[0] for row in cursor.execute("SELECT WrkHr FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "Dept": [row[0] for row in cursor.execute("SELECT Dept FROM Payroll WHERE EID = %s", (target_eid,)) or cursor.fetchall()]
#         },
#         "Tax": {
#             "EID": [row[0] for row in cursor.execute("SELECT EID FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "Salary": [row[0] for row in cursor.execute("SELECT Salary FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "Type": [row[0] for row in cursor.execute("SELECT Type FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()],
#             "Tax": [row[0] for row in cursor.execute("SELECT Tax FROM Tax WHERE EID = %s", (target_eid,)) or cursor.fetchall()]
#         }
#     }

#     connection.close()
#     return database_state


# def filter_data(database_state, delset):
#     return {
#         table: {
#             col: [value for value in table_data[col] if value is not None]
#             for col in table_data.keys() if col in delset and f"{table}.{col}" != "Tax.Salary"
#         }
#         for table, table_data in database_state.items()
#     }


def get_target_cell_location(database_state, target_eid):
    for table, columns in database_state.items():
        if "Salary" in columns and columns["Salary"] == [None]:
            return {"table": table, "column": "Salary", "row": target_eid}
    return None


if __name__ == "__main__":
    generator = DataGenerator(num_entries=10)
    generator.generate_all()



    # print("Filtered Data:", filtered_data)
    # print("Target Cell Location:", target_cell_location)
