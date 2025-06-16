import pandas as pd
import mysql.connector
import argparse
import sys
import os

# allow imports from project root if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def execute_ddl_from_file(cursor, path):
    with open(path, 'r') as f:
        # read entire file, split on semicolons
        statements = f.read().split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if not stmt:
            continue
        cursor.execute(stmt)


class AdultDatasetCleaner:
    def __init__(self, input_file, ddl_file, insert_sql_file, host='localhost', user='root', password='uci@dbh@2084', database=None):
        self.input_file = input_file
        self.ddl_file = ddl_file
        self.insert_sql_file = insert_sql_file
        self.df = None
        self.df_cleaned = None

        self.mysql_config = {
            'host': host,
            'user': user,
            'password': password,
            'ssl_disabled': True
        }
        # Derive database name from input file (remove extension and path) or use provided database name
        self.mysql_db_name = database if database else os.path.splitext(os.path.basename(input_file))[0]

    def get_db_connection(self, database=None):
        config = self.mysql_config.copy()
        if database:
            config['database'] = database
        return mysql.connector.connect(**config)
    
    def load_data(self):
        self.df = pd.read_csv(self.input_file)

    def clean_data(self):
        self.df.replace('?', pd.NA, inplace=True)
        self.df_cleaned = self.df.dropna().reset_index(drop=True)

    def save_cleaned_data(self):
        # Ensure the database exists
        mysql_con = self.get_db_connection()
        mysql_cur = mysql_con.cursor()
        mysql_cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.mysql_db_name}")
        mysql_con.commit()
        mysql_con.close()
        print(f"Database '{self.mysql_db_name}' created/verified")

        # Connect to the specific database
        mysql_con = self.get_db_connection(database=self.mysql_db_name)
        mysql_cur = mysql_con.cursor()
        print(f"Connected to database '{self.mysql_db_name}'")

        # Create table using provided DDL file
        execute_ddl_from_file(mysql_cur, self.ddl_file)
        mysql_con.commit()
        print(f"DDL executed from '{self.ddl_file}'")

        # Read insert SQL from provided file
        with open(self.insert_sql_file, 'r') as f:
            content = f.read()
            # Remove SQL comments and clean up
            lines = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('--'):
                    lines.append(line)
            insert_sql = ' '.join(lines).strip().rstrip(';')
        print(f"INSERT SQL: {insert_sql}")
        
        # Debug: Check data structure
        print(f"DataFrame columns: {list(self.df_cleaned.columns)}")
        print(f"DataFrame shape: {self.df_cleaned.shape}")
        print(f"First row data: {tuple(self.df_cleaned.iloc[0])}")
        print(f"First row length: {len(tuple(self.df_cleaned.iloc[0]))}")

        # Insert data into the table
        inserted_count = 0
        try:
            for _, row in self.df_cleaned.iterrows():
                row_data = tuple(row)
                mysql_cur.execute(insert_sql, row_data)
                inserted_count += 1
                if inserted_count % 1000 == 0:
                    print(f"Inserted {inserted_count} rows...")
                # Debug first few insertions
                if inserted_count <= 3:
                    print(f"Row {inserted_count}: {row_data}")
                    
        except Exception as e:
            print(f"Error during insertion at row {inserted_count + 1}: {e}")
            print(f"Problematic row data: {tuple(row) if 'row' in locals() else 'N/A'}")
            mysql_con.rollback()
            mysql_cur.close()
            mysql_con.close()
            raise

        # Commit and close connection
        mysql_con.commit()
        print(f"Successfully inserted {inserted_count} rows and committed to database")
        
        # Verify data was inserted
        mysql_cur.execute("SELECT COUNT(*) FROM adult_data")
        count = mysql_cur.fetchone()[0]
        print(f"Verification: {count} rows found in table")
        
        mysql_cur.close()
        mysql_con.close()

    def print_summary(self):
        print("Original shape:", self.df.shape)
        print("Cleaned shape:", self.df_cleaned.shape)

    def process(self):
        self.load_data()
        self.clean_data()
        self.save_cleaned_data()
        self.print_summary()


def main():
    parser = argparse.ArgumentParser(description='Clean Adult dataset and save to MySQL database')
    parser.add_argument('input_file', help='Path to the input CSV file (adult.csv)')
    parser.add_argument('ddl_file', help='Path to the DDL SQL file for table creation')
    parser.add_argument('insert_sql_file', help='Path to the INSERT SQL file')
    
    # Optional arguments
    parser.add_argument('--host', default='localhost', help='MySQL host (default: localhost)')
    parser.add_argument('--user', default='root', help='MySQL user (default: root)')
    parser.add_argument('--password', default='uci@dbh@2084', help='MySQL password')
    parser.add_argument('--database', help='MySQL database name (default: derived from input filename)')
    
    args = parser.parse_args()
    
    # Validate file existence
    for file_path in [args.input_file, args.ddl_file, args.insert_sql_file]:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' does not exist.")
            sys.exit(1)
    
    # Create cleaner instance with all parameters
    cleaner = AdultDatasetCleaner(
        input_file=args.input_file,
        ddl_file=args.ddl_file, 
        insert_sql_file=args.insert_sql_file,
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    try:
        cleaner.process()
        print("Data processing completed successfully!")
    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()