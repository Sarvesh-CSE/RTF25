import pandas as pd
import random

class DataGenerator:
    def __init__(self, num_entries=10):
        self.num_entries = num_entries
        self.roles = [1, 2, 3, 4, 5] # Employee roles with increasing seniority
        self.states = ['NC', 'CA', 'NY', 'TX', 'FL']
        self.zips = [27708, 95616, 10001, 73301, 33101]
        self.depts = ['CS', 'Eng', 'HR', 'Sales']
        self.employee_data = []
        self.payroll_data = []
        self.tax_data = []

    def generate_employee_data(self):
        self.employee_data = [
            {
                'EId': i,
                'Name': f'Employee_{i}',
                'ZIP': random.choice(self.zips),
                'State': random.choice(self.states),
                'Role': random.choice(self.roles) # Role assigned randomly
            }
            for i in range(1, self.num_entries + 1)
        ]

    def generate_payroll_data(self):
        self.payroll_data = [
            {
                'EId': i,
                # Ensures 𝜙₄: Role 1 cannot have SalPrHr > 100
                'SalPrHr': random.randint(50, 100) if emp['Role'] == 1 else random.randint(100 * emp['Role'], 200 * emp['Role']),
                'WrkHr': random.randint(20, 40),
                'Dept': random.choice(self.depts)
            }
            for i, emp in enumerate(self.employee_data, start=1)
        ]

        self.tax_data = [
            {
                'EId': i,
                # Ensures 𝜙₃: Salary is correctly calculated
                'Salary': (salary := emp['SalPrHr'] * emp['WrkHr']),
                'Type': 'Full' if salary >= 5000 else 'Part',
                'Tax': int(salary * 0.2)  # Tax calculated as 20% of salary
            }
            for i, emp in enumerate(self.payroll_data, start=1)
        ]

    def export_to_csv(self):
        pd.DataFrame(self.employee_data).to_csv('employee.csv', index=False)
        pd.DataFrame(self.payroll_data).to_csv('payroll.csv', index=False)
        pd.DataFrame(self.tax_data).to_csv('tax.csv', index=False)

        print("Employee Table:\n", pd.DataFrame(self.employee_data).head())
        print("\nPayroll Table:\n", pd.DataFrame(self.payroll_data).head())
        print("\nTax Table:\n", pd.DataFrame(self.tax_data).head())

    def generate_all(self):
        self.generate_employee_data()
        self.generate_payroll_data()
        self.generate_tax_data()
        self.export_to_csv()

# Generate and export the data
if __name__ == "__main__":
    generator = DataGenerator(num_entries=10)
    generator.generate_all()