import sqlite3

import mysql.connector

# Connect to the MySQL database
connection = mysql.connector.connect(
            host='localhost',        # Localhost for local MySQL instance
            user='root',    # Your MySQL username (e.g., root)
            password='uci@dbh@2084',# Your MySQL password
            database='RTF25' # Database you want to connect to
        )

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Example query to fetch a specific cell from a table
cursor.execute("SELECT * FROM Tax WHERE EId =2")
result = cursor.fetchone()

# Print the result
if result:
    print(result)

# Close the connection
cursor.close()
connection.close()

