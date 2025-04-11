import mysql.connector

class AttributeDomainComputation:
    def __init__(self):
          pass

    def get_db_connection(self):
            return mysql.connector.connect(
                host='localhost',
                user='root',
                password='uci@dbh@2084',
                database='RTF25'
            )

    def compute_attribute_domain(self):
        connection = self.get_db_connection()
        cursor = connection.cursor()

        db_name = 'RTF25'
        tables = ['Employee', 'Payroll', 'Tax']
        
        numeric_types = {'int', 'bigint', 'smallint', 'decimal', 'float', 'double', 'numeric', 'real'}
        string_types = {'varchar', 'char', 'text', 'enum', 'set'}

        print("Attribute Domains:\n")

        for table in tables:
            print(f"Table: {table}")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (db_name, table))
            
            columns = cursor.fetchall()

            for column_name, data_type in columns:
                data_type = data_type.lower()
                if data_type in numeric_types:
                    cursor.execute(f"""
                        SELECT MIN({column_name}) AS min_val, MAX({column_name}) AS max_val
                        FROM {table}
                    """)
                    min_val, max_val = cursor.fetchone()
                    print(f"  {column_name} [NUMERIC] -> Min: {min_val}, Max: {max_val}")

                elif data_type in string_types:
                    cursor.execute(f"""
                        SELECT DISTINCT {column_name}
                        FROM {table}
                        WHERE {column_name} IS NOT NULL
                        ORDER BY {column_name}
                    """)
                    values = [row[0] for row in cursor.fetchall()]
                    print(f"  {column_name} [STRING] -> Values: {values}")

            print("-" * 60)

        cursor.close()
        connection.close()

if __name__ == "__main__":
    ad_computation = AttributeDomainComputation()
    ad_computation.compute_attribute_domain()
