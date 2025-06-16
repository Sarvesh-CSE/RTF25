-- sql/insert_hospital_data.sql

INSERT INTO `hospital_data` (
  `ProviderNumber`, 
  `HospitalName`, 
  `City`, 
  `State`, 
  `ZIPCode`, 
  `CountyName`, 
  `PhoneNumber`, 
  `HospitalType`, 
  `HospitalOwner`, 
  `EmergencyService`, 
  `Condition`, 
  `MeasureCode`, 
  `MeasureName`, 
  `Sample`, 
  `StateAvg`
) VALUES (
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s
);