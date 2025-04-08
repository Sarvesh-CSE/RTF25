import mysql.connector

# Global declaration of delset and target_eid
delset = {"Salary", "Tax", "Role", "WrkHr"}
target_eid = 2

def fetch_database_state(target_eid, delset):
    """
    Fetch the database state for the target EID from the Employee, Payroll, and Tax tables.

    :param target_eid: The EID of the target employee
    :param delset: The set of columns to include in the result
    :return: A dictionary of tables and columns
    """
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='uci@dbh@2084',
        database='RTF25'
    )
    cursor = connection.cursor()

    if "Salary" in delset:
         cursor.execute("UPDATE Tax SET Salary = NULL WHERE EID = %s", (target_eid,))
         connection.commit()
         print(f"Salary for EID {target_eid} has been set to NULL.")
    # Fetch the state of Employee, Payroll, and Tax tables for the given EID
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
    cursor.close()
    connection.close()
    return database_state

def filter_data(database_state, delset):
    """
    Filters the data based on delset and ensures relevant columns are returned.

    :param database_state: The state of the database retrieved from `fetch_database_state`
    :param delset: The set of columns to include in the result
    :return: Filtered data in the same structure as database_state
    """
    filtered_data = {}
    for table_name, table_data in database_state.items():
        filtered_data[table_name] = {
            col: [value for value in table_data[col] if value is not None]
            for col in table_data.keys() if col in delset
        }
    return filtered_data

def get_target_cell_location(database_state, target_eid):
    """
    Determines the location of the target cell based on database state and the target EID.

    :param database_state: The state of the database retrieved from `fetch_database_state`
    :param target_eid: The EID of the target employee
    :return: Location of the target cell (table, column, row)
    """
    target_cell_location = None
    for table_name, columns in database_state.items():
        if table_name == "Tax":
            if "Salary" in columns:
                for i, value in enumerate(columns["Salary"]):
                    if value is None:
                        target_cell_location = {"table": table_name, "column": "Salary", "row": target_eid}
                        break
    return target_cell_location

# You can add more functions or logic as necessary



# # Update the Salary of EID 2 to NULL in the Tax table
# database_state = fetch_database_state(target_eid, delset)
# print("Database State:", database_state)
# filtered_data = filter_data(database_state, delset) 
# print("Filtered Data:", filtered_data)
# target_cell_location = get_target_cell_location(database_state, target_eid)
# print("Target Cell Location:", target_cell_location)

