-- ddl/adult_data.sql
CREATE TABLE IF NOT EXISTS `adult_data` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `age` INT,
  `workclass` VARCHAR(255),
  `fnlwgt` INT,
  `education` VARCHAR(255),
  `education_num` INT,
  `marital_status` VARCHAR(255),
  `occupation` VARCHAR(255),
  `relationship` VARCHAR(255),
  `race` VARCHAR(255),
  `sex` VARCHAR(255),
  `capital_gain` INT,
  `capital_loss` INT,
  `hours_per_week` INT,
  `native_country` VARCHAR(255),
  `income` VARCHAR(255)
) 
