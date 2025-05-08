denial_constraints = {
    "𝜙1": ["Customer", "Supplier"],
    "𝜙2": ["Receiptdate", "Shipdate"],
    "𝜙3": ["ExtPrice", "Discount"],
    "𝜙4": ["Qty", "Tax", "ExtPrice", "Discount"]
}

# ¬(t.Customer = t′.Supplier ∧ t.Supplier = t′.Customer)
# ¬(t.Receiptdate ≥ t′.Shipdate ∧ t.Shipdate ≤ t′.Receiptdate)
# ¬(t.ExtPrice > t′.ExtPrice ∧ t.Discount < t′.Discount)
# ¬(t.Qty = t′.Qty ∧ t.Tax = t′.Tax ∧ t.ExtPrice > t′.ExtPrice ∧ t.Discount < t′.Discount)


