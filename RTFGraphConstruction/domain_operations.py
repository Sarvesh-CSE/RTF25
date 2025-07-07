# File: domain_operations.py

from typing import Tuple, List, Optional

class NumericalDomain:
    """Simple class to handle numerical domain operations"""
    
    def __init__(self, lower_bound: float, upper_bound: float):
        self.lower = lower_bound
        self.upper = upper_bound
    
    def size(self) -> float:
        """Get the size of the domain range"""
        return self.upper - self.lower
    
    def restriction_level(self) -> float:
        """Higher value = more restricted (smaller range)"""
        return 1.0 / (self.size() + 1e-10)
    
    def __str__(self):
        return f"({self.lower}, {self.upper})"
    
    def __repr__(self):
        return self.__str__()

def intersect_domains(domain1: NumericalDomain, domain2: NumericalDomain) -> NumericalDomain:
    """Intersect two numerical domains"""
    new_lower = max(domain1.lower, domain2.lower)
    new_upper = min(domain1.upper, domain2.upper)
    return NumericalDomain(new_lower, new_upper)

def union_domains(domain1: NumericalDomain, domain2: NumericalDomain) -> NumericalDomain:
    """Union of two numerical domains"""
    new_lower = min(domain1.lower, domain2.lower)
    new_upper = max(domain1.upper, domain2.upper)
    return NumericalDomain(new_lower, new_upper)

def compute_overlap_distance(domain1: NumericalDomain, domain2: NumericalDomain) -> float:
    """Compute overlap distance between two domains (0 = identical, 1 = no overlap)"""
    # Intersection
    intersection_lower = max(domain1.lower, domain2.lower)
    intersection_upper = min(domain1.upper, domain2.upper)
    intersection_size = max(0, intersection_upper - intersection_lower)
    
    # Union
    union_lower = min(domain1.lower, domain2.lower)
    union_upper = max(domain1.upper, domain2.upper)
    union_size = union_upper - union_lower
    
    if union_size == 0:
        return 0.0
    
    # Jaccard distance = 1 - (intersection / union)
    return 1.0 - (intersection_size / union_size)

# Test this module
if __name__ == "__main__":
    # Test basic operations
    domain1 = NumericalDomain(10, 20)
    domain2 = NumericalDomain(15, 25)
    
    print(f"Domain 1: {domain1}, size: {domain1.size()}, restriction: {domain1.restriction_level():.4f}")
    print(f"Domain 2: {domain2}, size: {domain2.size()}, restriction: {domain2.restriction_level():.4f}")
    
    intersection = intersect_domains(domain1, domain2)
    union = union_domains(domain1, domain2)
    overlap = compute_overlap_distance(domain1, domain2)
    
    print(f"Intersection: {intersection}")
    print(f"Union: {union}")
    print(f"Overlap distance: {overlap:.4f}")