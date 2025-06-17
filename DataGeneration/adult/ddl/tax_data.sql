-- ddl/tax_data.sql
CREATE TABLE IF NOT EXISTS `tax_data` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `fname` VARCHAR(100),
  `lname` VARCHAR(100),
  `gender` CHAR(1),
  `area_code` CHAR(3),
  `phone` VARCHAR(20),
  `city` VARCHAR(100),
  `state` CHAR(2),
  `zip` VARCHAR(10),
  `marital_status` CHAR(1),
  `has_child` CHAR(1),
  `salary` INT,
  `rate` DECIMAL(8,6),
  `single_exemp` INT,
  `married_exemp` INT,
  `child_exemp` INT
);
