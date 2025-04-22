from proess_data import fetch_database_state, filter_data, get_target_cell_location, delset, target_eid
from dc_lookup import generate_lookup_table
from IGC_c_get_global_domain_mysql import AttributeDomainComputation

class InferenceGraph:
    def __init__(self, db_state, delset, lookup_table, default_domains):
        self.db_state = db_state
        self.delset = delset
        self.lookup_table = lookup_table
        self.default_domains = default_domains
        self.graph = {}
        self.inferred_domains = {}
        self.memoization = {}

    def build_graph(self):
        # Step 1: Initialize graph and inferred domains
        for cell in self.delset:
            # Initialize the adjacency list for each cell
            self.graph[cell] = set()
            
            # Step 2: Initialize inferred domain for non-NULL cells
            if self.db_state[cell] is not None:
                self.inferred_domains[cell] = {self.db_state[cell]}  # Use set instead of list
            else:
                # For NULL cells, use the default domain for the attribute
                self.inferred_domains[cell] = self.default_domains[cell]
        
        # Step 3: Build the graph based on the lookup table and denial constraints
        for cell in self.delset:
            for constraint in self.lookup_table.get(cell, []):
                for neighbor in self.delset:
                    if neighbor != cell and any(attr in constraint for attr in self.lookup_table.get(neighbor, [])):
                        self.graph[cell].add(neighbor)
                        self.graph[neighbor].add(cell)

    def get_bounds(self, cell, partial_domain, constraint):
        # This is a placeholder function, it should compute the domain bounds
        # after applying the given denial constraint to the cell.
        # In reality, this would be more complex depending on the type of constraint.
        return partial_domain

    def build_inferred_domains(self):
        # Step 4: Start the iterative process to propagate constraints and refine domains
        changed = True
        while changed:
            changed = False
            for cell in self.delset:
                partial_results = []
                for constraint in self.lookup_table.get(cell, []):
                    # Step 5: Retrieve or compute partial domain restrictions for the constraint
                    # Convert the set 'constraint' into a frozenset
                    frozen_constraint = frozenset(constraint)

                    # Memoization lookup now uses frozenset as key
                    if (cell, frozen_constraint) in self.memoization:
                        partial_domain = self.memoization[(cell, frozen_constraint)]
                    else:
                        partial_domain = self.get_bounds(cell, self.inferred_domains[cell], frozen_constraint)
                        self.memoization[(cell, frozen_constraint)] = partial_domain
                    
                    partial_results.append(partial_domain)

                # Step 6: Combine partial results using union and intersect with current inferred domain
                combined = partial_results[0]
                for result in partial_results[1:]:
                    combined = combined.union(result)
                new_inferred_domain = self.inferred_domains[cell].intersection(combined)

                # Step 7: If domain has changed, update and continue iteration
                if new_inferred_domain != self.inferred_domains[cell]:
                    self.inferred_domains[cell] = new_inferred_domain
                    changed = True

    def get_inference_graph_and_domains(self):
        return self.graph, self.inferred_domains


# Example Data (for demonstration)
db_state = {
    "Tax": 1000,
    "Salary": None,
    "Role": "Manager",
    "SalPrHr": None,
    "WrkHr": 40
}
lookup_table = generate_lookup_table()

default_domains = {
    "Salary": {3000, 4000, 5000},  # Possible values for Salary (set for categorical type)
    "SalPrHr": {10, 20, 30},
    "WrkHr": {20, 40, 60}
}

# Load domain map from file
adc = AttributeDomainComputation()
adc.load_domain_map("domain_map.json")  # Assuming it's already generated

# Build default_domains for NULL attributes
default_domains = {}
for attr in delset:
    if db_state[attr] is None:
        domain_info = adc.get_domain("Payroll", attr)  # 🔁 Replace 'Payroll' with the correct table
        if domain_info["type"] == "numeric":
            min_val, max_val = domain_info["min"], domain_info["max"]
            default_domains[attr] = set(range(int(min_val), int(max_val) + 1))
        elif domain_info["type"] == "string":
            default_domains[attr] = set(domain_info["values"])





# Instantiate the InferenceGraph class
inference_graph = InferenceGraph(db_state, delset, lookup_table, default_domains)

# Step 1: Build the inference graph based on given data
inference_graph.build_graph()

# Step 2: Build inferred domains by applying constraints iteratively
inference_graph.build_inferred_domains()

# Step 3: Output the resulting inference graph and inferred domains
graph, inferred_domains = inference_graph.get_inference_graph_and_domains()

print("Inference Graph:", graph)
print("Inferred Domains:", inferred_domains)
