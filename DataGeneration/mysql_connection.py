import mysql.connector
from mysql.connector import Error

def connect_to_database():
    try:
        # Establish connection to the MySQL server
        connection = mysql.connector.connect(
            host='localhost',        # Localhost for local MySQL instance
            user='root',    # Your MySQL username (e.g., root)
            password='uci@dbh@2084',# Your MySQL password
            database='RTF25' # Database you want to connect to
        )
 
        # Check if the connection is successful
        if connection.is_connected():
            print("Successfully connected to the database")

            # Create a cursor object to interact with the database
            cursor = connection.cursor()

            # Example: Query to fetch all tables in the database
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Tables in the database:")
            for table in tables:
                print(table)

        else:
            print("Connection failed")

    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if connection.is_connected():
            # Close the connection
            cursor.close()
            connection.close()
            print("Connection closed")

if __name__ == "__main__":
    connect_to_database()
