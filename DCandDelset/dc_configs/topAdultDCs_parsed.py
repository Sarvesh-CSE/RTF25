# Parsed denial constraints for Adult
# Generated automatically from raw constraints

denial_constraints = [
    [('t1.education', '!=', 't2.education'), ('t1.education_num', '==', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '!=', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '>', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '<', 't2.education_num')],
    [('t1.capital_gain', '>', 't2.capital_gain'), ('t1.capital_loss', '>', 't2.capital_loss')],
    [('t1.capital_gain', '<', 't2.capital_gain'), ('t1.capital_loss', '<', 't2.capital_loss')],
    [('t1.age', '==', 't2.age'), ('t1.fnlwgt', '==', 't2.fnlwgt'), ('t1.relationship', '==', 't2.relationship'), ('t1.sex', '!=', 't2.sex'), ('t1.native_country', '==', 't2.native_country')],
    [('t1.age', '==', 't2.age'), ('t1.fnlwgt', '==', 't2.fnlwgt'), ('t1.education', '==', 't2.education'), ('t1.occupation', '!=', 't2.occupation'), ('t1.race', '!=', 't2.race')],
]
