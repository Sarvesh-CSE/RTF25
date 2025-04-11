import mysql.connector

class AttributeDomainComputation:
    def __init__(self):
        self.domain_map = {}

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


        for table in tables:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """, (db_name, table))
            
            columns = cursor.fetchall()

            for column_name, data_type in columns:
                data_type = data_type.lower()
                key = (table, column_name)

                if data_type in numeric_types:
                    cursor.execute(f"""
                        SELECT MIN({column_name}), MAX({column_name})
                        FROM {table}
                    """)
                    min_val, max_val = cursor.fetchone()
                    self.domain_map[key] = {
                        'type': 'numeric',
                        'min': min_val,
                        'max': max_val
                    }

                elif data_type in string_types:
                    cursor.execute(f"""
                        SELECT DISTINCT {column_name}
                        FROM {table}
                        WHERE {column_name} IS NOT NULL
                        ORDER BY {column_name}
                    """)
                    values = [row[0] for row in cursor.fetchall()]
                    self.domain_map[key] = {
                        'type': 'string',
                        'values': values
                    }


        cursor.close()
        connection.close()

    def get_domain(self, table, column):
        return self.domain_map.get((table, column))


if __name__ == "__main__":
    ad_computation = AttributeDomainComputation()
    ad_computation.compute_attribute_domain()

    # Example usage
    print("\nAccessing Domain:")
    print("Payroll.SalPrHr:", ad_computation.get_domain("Payroll", "SalPrHr"))
    print("Employee.State:", ad_computation.get_domain("Employee", "State"))
