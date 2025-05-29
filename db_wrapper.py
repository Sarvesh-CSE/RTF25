import mysql.connector

class DatabaseConfig:
    """Database configuration and connection management."""
    def __init__(self, host='localhost', user='root', password='uci@dbh@2084', database='adult'):
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
        """Establish database connection with dictionary cursor."""
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

class DatabaseWrapper:
    """Wrapper for database operations."""
    
    def __init__(self, db_config: DatabaseConfig):
        self.db = db_config

    def execute_query(self, query: str):
        """Execute a SQL query and return the results."""
        self.db.cursor.execute(query)
        return self.db.cursor.fetchall()
    
    def get_tuple(self, query: str, param: str):
        """ Fetch a single tuple based on given key in the query."""
        self.db.cursor.execute(query, (param,))
        result = self.db.cursor.fetchone()
        if result:
            return tuple(result.values())
        return None

    def close(self):
        """Close the database connection."""
        self.db.close()

# Example usage of DatabaseWrapper
# db_wrapper = DatabaseWrapper(DatabaseConfig())    

# result = db_wrapper.execute_query("SELECT * FROM adult_data LIMIT 2;")
# # Print the result of the query
# print(result)
# db_wrapper.close()
