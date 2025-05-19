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

        bounds = []
        for dc_index, dc in enumerate(target_dc_list):
            target_predicate = None
            other_preds = []

            # Identify target predicate and other predicates
            for predicate in dc:
                left_attr = predicate[0].split('.')[-1]
                if left_attr == target_column:
                    target_predicate = predicate
                else:
                    other_preds.append(predicate)

            if not target_predicate:
                print(f"No target predicate found in DC: {dc}")
                continue

            print(f"\nTarget predicate: {target_predicate}")
            print(f"Other predicates: {other_preds}")

            # Build WHERE clauses for LHS and RHS
            lhs_conditions = []
            rhs_conditions = []

            for pred in other_preds:
                left = pred[0].split('.')[-1]
                op = pred[1]
                right = pred[2].split('.')[-1]

                op_sql = '=' if op == '==' else op

                lhs_conditions.append(f"{left} {op_sql} {repr(target_tuple[right])}")
                rhs_conditions.append(f"{repr(target_tuple[left])} {op_sql} {right}")

            lhs_where_clause = " AND ".join(lhs_conditions)
            rhs_where_clause = " AND ".join(rhs_conditions)

            print(f"LHS WHERE clause: {lhs_where_clause}")
            print(f"RHS WHERE clause: {rhs_where_clause}")

            # Determine direction based on target predicate
            target_op = target_predicate[1]
            target_col_name = target_predicate[0].split('.')[-1]

            if target_op == '>':
                sql_query_left = f"SELECT MIN({target_col_name}) FROM {self.db.config['database']}.{table_name} WHERE {lhs_where_clause};"
                sql_query_right = f"SELECT MAX({target_col_name}) FROM {self.db.config['database']}.{table_name} WHERE {rhs_where_clause};"
            elif target_op == '<':#switched order of bounds for this operator
                sql_query_right = f"SELECT MAX({target_col_name}) FROM {self.db.config['database']}.{table_name} WHERE {lhs_where_clause};"
                sql_query_left = f"SELECT MIN({target_col_name}) FROM {self.db.config['database']}.{table_name} WHERE {rhs_where_clause};"
            else:
                # For unsupported operators, get both min and max as bounds
                sql_query_left = f"SELECT MIN({target_col_name}) FROM {self.db.config['database']}.{table_name} WHERE {lhs_where_clause};"
                sql_query_right= f"SELECT MAX({target_col_name}) FROM {self.db.config['database']}.{table_name} WHERE {rhs_where_clause};"

            print(f"SQL Query (left): {sql_query_left}")
            print(f"SQL Query (right): {sql_query_right}")

            # Execute both queries and collect bounds
            left_bound = self.execute_query(sql_query_left)
            right_bound = self.execute_query(sql_query_right)
            #bounds are (int, int). Ignore (None, None)
            if left_bound is None and right_bound is None:
                print(f"Skipping: Both bounds are None for DC index {dc_index}.")
                continue
            else:
                if left_bound is None:
                    left_bound = right_bound
                elif right_bound is None:
                    right_bound = left_bound
                bounds.append((left_bound, right_bound))
                print(f"Bounds for DC index {dc_index} and {dc}: {left_bound}, {right_bound}")
                

        print(f"\nAll bounds for {target_column}: {bounds}")
        self.intersect_bounds(bounds)
        return bounds
    
    def intersect_bounds(self, get_bound_list):
        # Compute the intersection of all bounds in get_bound_list
        # Each element in get_bound_list is a tuple: (bound1, bound2)
        # The intersection is [max(min(bound1, bound2)), min(max(bound1, bound2))]

        intersect = (max(get_bound_list,  key=lambda x: x[0])[0], min(get_bound_list,  key=lambda x: x[0])[0])
        # min_bounds = []
        # max_bounds = []
        # for b in get_bound_list:
        #     if b[0] is not None and b[1] is not None:
        #         min_bounds.append(min(b[0], b[1]))
        #         max_bounds.append(max(b[0], b[1]))
        # if not min_bounds or not max_bounds:
        #     return None, None
        # intersection_min = max(min_bounds)
        # intersection_max = min(max_bounds)
        # if intersection_min > intersection_max:
        #     # No intersection
        #     return None, None
        print(f"Final bounds: {intersect}")
        return intersect

        
    def execute_query(self, query):
        cursor = self.db.cursor
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            # Get the first value from the dictionary
            return next(iter(result.values()))
        else:
            return None



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get bounds for a specific column in a table.")
    parser.add_argument("--table_name", type=str, default='adult_data', help="Name of the table")
    parser.add_argument("--target_column_name", type=str, default='fnlwgt', help="Name of the column")
    parser.add_argument("--key_column_name", type=str, default='id', help="Primary key column name")
    parser.add_argument("--key_value", type=str, default='4', help="Primary key value")
    args = parser.parse_args()

    domain_infer = DomianInferFromDC()
    domain_infer.get_target_column_type(args.table_name, args.target_column_name)
    target_dc_list = domain_infer.get_target_dc_list(args.table_name, args.target_column_name)
    target_tuple =domain_infer.get_target_tuple(args.table_name, args.key_column_name, key_value='4')  # Example key value
    bound_list = domain_infer.get_bound_from_DC(target_dc_list=target_dc_list,
                                    target_tuple=target_tuple,
                                      table_name=args.table_name,
                                      target_column=args.target_column_name) 
    intersect = domain_infer.intersect_bounds(bound_list)

    

    

