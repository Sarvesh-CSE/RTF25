-- sql/insert_adult_data.sql
INSERT INTO `adult_data` (
  age, workclass, fnlwgt, education, education_num,
  marital_status, occupation, relationship, race, sex,
  capital_gain, capital_loss, hours_per_week, native_country, income
) VALUES (
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s
);
