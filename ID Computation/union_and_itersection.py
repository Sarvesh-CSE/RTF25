# domain_helpers.py

from typing import List, Tuple

Interval = Tuple[int, int]  # A numerical range

def union_ranges(R1: List[Interval], R2: List[Interval]) -> List[Interval]:
    merged = []
    for start, end in sorted(R1 + R2):
        if merged and start <= merged[-1][1]:  # Merge overlaps
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged

def intersect_ranges(R1: List[Interval], R2: List[Interval]) -> List[Interval]:
    result = []
    i, j = 0, 0
    while i < len(R1) and j < len(R2):
        a, b = R1[i]
        c, d = R2[j]
        low, high = max(a, c), min(b, d)
        if low <= high:
            result.append((low, high))
        if b < d:
            i += 1
        else:
            j += 1
    return result



# EXAMPLES
if __name__ == "__main__":
    # Intersect and Union example
    R1 = [(1, 5), (10, 15)]
    R2 = [(3, 12)]
    print("Union:", union_ranges(R1, R2))  # [(1, 15)]
    print("Intersect:", intersect_ranges(R1, R2))  # [(3, 5), (10, 12)]


 