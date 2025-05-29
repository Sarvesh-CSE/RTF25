from typing import List, Tuple
import pandas as pd
import operator

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path
from DCandDelset.dc_configs.topAdultDCs_parsed import denial_constraints # Import parsed denial constraints
from IDcomputation.IGC_d_getBounds import DatabaseConfig


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


# Create two Attribute objects
a1 = Attribute("Employee", "salary")
a2 = Attribute("Employee", "salary")
b  = Attribute("Employee", "age")

# Printing
print(a1)            # → Employee.salary

# Equality
print(a1 == a2)      # → True
print(a1 == b)       # → False

# Using in a set or dict
attrs = {a1, b}
print(a2 in attrs)   # → True   (because a2 hashes equal to a1)


# Create an Attribute and two Cells
attr = Attribute("Person", "salary")
c1 = Cell(attr, key=101, value=70000)
c2 = Cell(Attribute("Person","salary"), key=101, value=70000)

# Even though c1 and c2 are different objects:
print(c1 == c2)         # → True
print({c1, c2})         # → only one element in the set

# Inspecting:
print(c1)               # → Person.salary[101]=>70000
