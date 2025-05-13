import pandas as pd
import mysql.connector

class AdultDatasetCleaner:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.df = None
        self.df_cleaned = None

        self.mysql_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'uci@dbh@2084',
            'ssl_disabled': True
        }
        self.mysql_db_name = 'adult'

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

        # Connect to the specific database
        mysql_con = self.get_db_connection(database=self.mysql_db_name)
        mysql_cur = mysql_con.cursor()

        # Create table if it doesn't exist
        mysql_cur.execute("""
        CREATE TABLE IF NOT EXISTS adult_data (
            age INT,
            workclass VARCHAR(255),
            fnlwgt INT,
            education VARCHAR(255),
            education_num INT,
            marital_status VARCHAR(255),
            occupation VARCHAR(255),
            relationship VARCHAR(255),
            race VARCHAR(255),
            sex VARCHAR(255),
            capital_gain INT,
            capital_loss INT,
            hours_per_week INT,
            native_country VARCHAR(255),
            income VARCHAR(255)
        )
        """)

        # Insert data into the table
        for _, row in self.df_cleaned.iterrows():
            mysql_cur.execute("""
            INSERT INTO adult_data (
                age, workclass, fnlwgt, education, education_num, marital_status, 
                occupation, relationship, race, sex, capital_gain, capital_loss, 
                hours_per_week, native_country, income
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(row))

        # Commit and close connection
        mysql_cur.close()
        mysql_con.commit()
        mysql_con.close()

    def print_summary(self):
        print("Original shape:", self.df.shape)
        print("Cleaned shape:", self.df_cleaned.shape)
        print(f"Saved as '{self.output_file}'")

    def process(self):
        self.load_data()
        self.clean_data()
        self.save_cleaned_data()
        self.print_summary()

# Usage
if __name__ == "__main__":
    cleaner = AdultDatasetCleaner("adult.csv", "adult_cleaned.csv")
    cleaner.process()
