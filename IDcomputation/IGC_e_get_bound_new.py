import mysql.connector
import json
import os
import argparse
import sys

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path

from IGC_c_get_global_domain_mysql import AttributeDomainComputation
from IGC_d_getBounds import DatabaseConfig
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints

class DomianInferFromDC:
    def __init__(self, db_name='adult'):
        self.db = DatabaseConfig(database=db_name)

    def get_target_column_type(self, table_name, column_name):
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
    
    def get_target_tuple(self, table_name, key_attr, key_value):
        # Get the target tuple from the database
        cursor = self.db.cursor
        cursor.execute(f"""
            SELECT *
            FROM {table_name}
            WHERE {key_attr} = '{key_value}'
        """)
        result = cursor.fetchone()
        print(result['age'])
        return result          

    def get_bound_from_DC(self, dc_list, target_tuple):
        # for dc_index, dc in enumerate(dc_list):
        #     if dc. 
        #         return dc.bound
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get bounds for a specific column in a table.")
    parser.add_argument("table_name", type=str, help="Name of the table")
    parser.add_argument("target_column_name", type=str, help="Name of the column")
    parser.add_argument("--key_column_name", type=str, default='id', help="Primary key column name")
    parser.add_argument("--key_value", type=str, default='4', help="Primary key value")
    args = parser.parse_args()

    domain_infer = DomianInferFromDC()
    domain_infer.get_target_column_type(args.table_name, args.target_column_name)
    target_tuple =domain_infer.get_target_tuple(args.table_name, args.key_column_name, key_value='4')  # Example key value
    domain_infer.get_bound_from_DC(denial_constraints, target_tuple=target_tuple) 

    

    

