import mysql.connector
import json
import os
import argparse
import sys

# Add each subfolder to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))  # Path to project_root

sys.path.append(os.path.join(base_dir, 'DCandDelset/dc_configs'))
sys.path.append(os.path.join(base_dir, 'IDcomputation'))


from IGC_c_get_global_domain_mysql import AttributeDomainComputation
from IGC_d_getBounds import DatabaseConfig
from 

sys.path.append(os.path.abspath('../DCandDelset/dc_config'))

class DomianInferFromDC:
    def __init__(self, db_name='RTF25'):
        self.db = DatabaseConfig(database=db_name)

    def get_column_type(self, table_name, column_name):
        cursor = self.db.cursor # using the cursor from the db class
        # Get the data type of the column
        cursor.execute(f"""
            SELECT DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{self.db.config['database']}' AND TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{column_name}'
        """)
        result = cursor.fetchone()
        if result:
            data_type = result['DATA_TYPE']
            data_type = data_type.lower()
            print(f"Data type for {table_name}.{column_name}: {data_type}")
        else:
            print(f"No data type found for {table_name}.{column_name}")
    
    def get_bound_from_DC(self, dc_list, target_tuple):
        for dc in dc_list:
            if dc.target_tuple == target_tuple:
                return dc.bound
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get bounds for a specific column in a table.")
    parser.add_argument("table_name", type=str, help="Name of the table")
    parser.add_argument("column_name", type=str, help="Name of the column")
    args = parser.parse_args()

    domain_infer = DomianInferFromDC()
    domain_infer.get_column_type(args.table_name, args.column_name)  

    

    

