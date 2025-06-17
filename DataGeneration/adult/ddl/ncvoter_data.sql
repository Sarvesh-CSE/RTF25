-- ddl/voter_data.sql
CREATE TABLE IF NOT EXISTS `ncvoter_data` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `voter_id` VARCHAR(20),
  `voter_reg_num` DECIMAL(15,2),
  `name_prefix` VARCHAR(10),
  `first_name` VARCHAR(100),
  `middle_name` VARCHAR(100),
  `last_name` VARCHAR(100),
  `name_suffix` VARCHAR(10),
  `age` INT,
  `gender` CHAR(1),
  `race` CHAR(1),
  `ethnic` VARCHAR(10),
  `street_address` VARCHAR(255),
  `city` VARCHAR(100),
  `state` CHAR(2),
  `zip_code` VARCHAR(10),
  `full_phone_num` VARCHAR(20),
  `birth_place` VARCHAR(50),
  `register_date` DATE,
  `download_month` VARCHAR(10)
);