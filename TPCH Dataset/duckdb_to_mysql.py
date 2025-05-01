import duckdb
import mysql.connector
import pandas as pd

class TPCHMigrator:
    def __init__(self):
        self.mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'uci@dbh@2084',
            'ssl_disabled': True
        }
        self.mysql_db_name = 'tpchDB'
        self.duckdb_path = 'tpch-sf1.db'
        self.batch_size = 10000

    def get_db_connection(self, database=None):
        config = self.mysql_config.copy()
        if database:
            config['database'] = database
        return mysql.connector.connect(**config)

    def clean_row(self, row):
        """Convert Timestamp to string, NaT to NULL."""
        return [
            None if pd.isna(val)
            else val.strftime('%Y-%m-%d %H:%M:%S') if isinstance(val, pd.Timestamp)
            else val
            for val in row
        ]

    def migrate(self):
        # Step 1: Read DuckDB tables
        duck_con = duckdb.connect(self.duckdb_path)
        table_names = [row[0] for row in duck_con.execute("SHOW TABLES").fetchall()]

        # Step 2: Create MySQL database
        mysql_con = self.get_db_connection()
        mysql_cur = mysql_con.cursor()
        mysql_cur.execute(f"DROP DATABASE IF EXISTS {self.mysql_db_name}")
        mysql_cur.execute(f"CREATE DATABASE {self.mysql_db_name}")
        mysql_con.commit()
        mysql_con.close()

        # Step 3: Reconnect to MySQL in target DB
        mysql_con = self.get_db_connection(self.mysql_db_name)
        mysql_cur = mysql_con.cursor()

        # Step 4: Migrate each table
        for table in table_names:
            df = duck_con.execute(f"SELECT * FROM {table}").fetchdf()
            columns = df.columns
            dtypes = df.dtypes

            # Create table schema
            schema = []
            for col, dtype in zip(columns, dtypes):
                if pd.api.types.is_integer_dtype(dtype):
                    sql_type = "INT"
                elif pd.api.types.is_float_dtype(dtype):
                    sql_type = "DOUBLE"
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    sql_type = "DATETIME"
                else:
                    sql_type = "TEXT"
                schema.append(f"`{col}` {sql_type}")
            schema_sql = ", ".join(schema)

            # Recreate MySQL table
            mysql_cur.execute(f"DROP TABLE IF EXISTS `{table}`")
            mysql_cur.execute(f"CREATE TABLE `{table}` ({schema_sql})")

            # Insert in batches
            insert_sql = f"INSERT INTO `{table}` VALUES ({', '.join(['%s'] * len(columns))})"
            rows = [self.clean_row(row) for row in df.itertuples(index=False, name=None)]

            for i in range(0, len(rows), self.batch_size):
                mysql_cur.executemany(insert_sql, rows[i:i + self.batch_size])
                mysql_con.commit()

            print(f"✅ Migrated `{table}` ({len(df)} rows)")

        mysql_cur.close()
        mysql_con.close()
        duck_con.close()
        print("🎉 All TPC-H tables migrated to MySQL successfully!")

if __name__ == "__main__":
    TPCHMigrator().migrate()
