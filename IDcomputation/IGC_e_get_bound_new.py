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
from DCandDelset import dc_lookup

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
    
    def get_target_dc_list(self, table_name, column_name):
        # Get the list of denial constraints for the specified column
        target_dc_list = []
        for dc in denial_constraints:
            for predicate in dc:
                # predicate[0] might be like 't2.education'
                pred_col = predicate[0].split('.')[-1]  # get column name without table alias
                if column_name == pred_col:
                    target_dc_list.append(dc)
                    break
        print(f"Denial constraints for {table_name}.{column_name}: {target_dc_list}")
        return target_dc_list

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
    
    def get_bound_from_DC(self, target_dc_list, target_tuple, target_column, table_name):
        if not isinstance(target_tuple[target_column], int):
            print(f"Skipping: '{target_column}' is not of type int.")
            return
            # Assuming the target column is an integer
        comparison_operators = ['>', '<']
        agg_func = {'>': 'MIN', '<': 'MAX'}
        for dc_index, dc in enumerate(target_dc_list):
                # Remove the predicate from dc that has the target attribute and store it as target_predicate
                target_predicate = None
                other_preds = []                    
                for predicate in dc:
                    left_attr = predicate[0].split('.')[-1]
                    if left_attr == target_column:
                        target_predicate = predicate
                    else:
                        other_preds.append(predicate)
                print(f"Target predicate: {target_predicate}")
                print(f"Other predicates: {other_preds}")
                # For each predicate in new_dc, generate two SQL queries
                # Build WHERE clause by combining all predicates in other_preds with AND
                lhs_where_clauses = []
                for pred in other_preds:
                    # Example: pred = ('t1.age', '>=', 't2.age')
                    left = pred[0].split('.')[-1]  # get column name without table alias
                    op = pred[1]
                    right = pred[2].split('.')[-1]  # get column name without table alias

                    lhs_where_clauses.append(f"{left} {op} {target_tuple[right]}")
                lhs_where_clauses = " AND ".join(lhs_where_clauses)
                print(f"LHS WHERE clause: {lhs_where_clauses}")
                
                
                # # Generate two queries: one for left, one for right
                # sql_query_left = f"SELECT MIN{target_predicate[0]} FROM {self.db.config['database']}.{table_name} WHERE {left} {op} {right};"
                # sql_query_right = f"SELECT MAX{target_predicate[0]} FROM {self.db.config['database']}.{table_name} WHERE {right} {op} {left};"
                # print(f"SQL Query (left): {sql_query_left}")
                # print(f"SQL Query (right): {sql_query_right}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get bounds for a specific column in a table.")
    parser.add_argument("--table_name", type=str, default='adult_data', help="Name of the table")
    parser.add_argument("--target_column_name", type=str, default='capital_loss', help="Name of the column")
    parser.add_argument("--key_column_name", type=str, default='id', help="Primary key column name")
    parser.add_argument("--key_value", type=str, default='4', help="Primary key value")
    args = parser.parse_args()

    domain_infer = DomianInferFromDC()
    domain_infer.get_target_column_type(args.table_name, args.target_column_name)
    target_dc_list = domain_infer.get_target_dc_list(args.table_name, args.target_column_name)
    target_tuple =domain_infer.get_target_tuple(args.table_name, args.key_column_name, key_value='4')  # Example key value
    domain_infer.get_bound_from_DC(target_dc_list=target_dc_list,
                                    target_tuple=target_tuple,
                                      table_name=args.table_name,
                                      target_column=args.target_column_name) 

    

    

