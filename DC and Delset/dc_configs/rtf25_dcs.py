denial_constraints = {
    "𝜙1": ["Tax", "Salary"],                    # ¬(t1.Tax > t2.Tax ∧ t1.Salary < t2.Salary)
    "𝜙2": ["Role", "SalPrHr"],                  # ¬(t1.Role > t2.Role ∧ t1.SalPrHr < t2.SalPrHr)
    "𝜙3": ["Salary", "SalPrHr", "WrkHr"],       # ¬(t1.Salary ≠ t1.SalPrHr × t1.WrkHr)
    "𝜙4": ["Role", "SalPrHr"]                   # ¬(t1.Role = 1 ∧ t1.SalPrHr > 100)
}





