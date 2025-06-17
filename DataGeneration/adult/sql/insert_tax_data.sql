-- sql/insert_employee_data.sql
INSERT INTO `tax_data` (
  `fname`, `lname`, `gender`, `area_code`, `phone`,
  `city`, `state`, `zip`, `marital_status`, `has_child`,
  `salary`, `rate`, `single_exemp`, `married_exemp`, `child_exemp`
) VALUES (
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s
);