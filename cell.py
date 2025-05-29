from typing import List, Tuple
import pandas as pd
import operator

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path
import db_wrapper as dbw

db_wrapper =dbw.DatabaseWrapper(dbw.DatabaseConfig())  # Initialize the database wrapper with the 'adult' database
# result =db_wrapper.execute_query("select * from adult_data limit 1;")  # Example query to fetch data from the 'adult_data' table
# print(result)  # Print the result of the query


sql_query = "select * from adult_data where id = %s limit 1;"  # SQL query to fetch a single tuple from the 'adult_data' table
target_tuple = db_wrapper.get_tuple(sql_query, 2)  # Fetch a single tuple from the 'adult_data' table
print(target_tuple)  # Print the fetched tuple

# 1) Core classes

class Attribute:
    def __init__(self, table: str, col: str):
        self.table = table
        self.col = col

    def __repr__(self):
        return f"{self.table}.{self.col}" # When you print an Attribute, it shows as table.col (e.g., users.id).

    def __eq__(self, other):
        return isinstance(other, Attribute) and (self.table, self.col) == (other.table, other.col)

    def __hash__(self):
        return hash((self.table, self.col))
    
class Cell:
    def __init__(self, attribute: Attribute, key, value):
        # 'attribute' is an instance of Attribute (e.g. Person.age)
        # 'key' uniquely identifies the tuple (e.g. a primary key or row index)
        # 'value' is the actual cell contents (e.g. 35 for age)
        self.attribute = attribute
        self.key = key
        self.value = value

    def __repr__(self):
        # Makes debugging easy:
        #   print(cell) → Person.age[123]=>35
        return f"{self.attribute}[{self.key}]=>{self.value}"

    def __eq__(self, other):
        # Two Cell objects are the same if they refer to the same
        # attribute, same tuple, and same value.
        return (
            isinstance(other, Cell) and
            (self.attribute, self.key, self.value) ==
            (other.attribute, other.key, other.value)
        )

    def __hash__(self):
        # Allow Cells to live in sets or be dict keys
        return hash((self.attribute, self.key, self.value))


