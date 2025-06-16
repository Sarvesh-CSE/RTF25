-- ddl/hospital_data.sql
CREATE TABLE IF NOT EXISTS `hospital_data` (
  `id`             INT AUTO_INCREMENT PRIMARY KEY,  
  `ProviderNumber` VARCHAR(20)    NOT NULL,
  `HospitalName`   VARCHAR(255)   NOT NULL,
  `City`           VARCHAR(100)   NOT NULL,
  `State`          CHAR(2)        NOT NULL,
  `ZIPCode`        VARCHAR(10)    NOT NULL,
  `CountyName`     VARCHAR(100)   NOT NULL,
  `PhoneNumber`    VARCHAR(20)    NOT NULL,
  `HospitalType`   VARCHAR(255)   NOT NULL,
  `HospitalOwner`  VARCHAR(255)   NOT NULL,
  `EmergencyService` VARCHAR(3)   NOT NULL,
  `Condition`      VARCHAR(255)   NOT NULL,
  `MeasureCode`    VARCHAR(50)    NOT NULL,
  `MeasureName`    TEXT           NOT NULL,
  `Sample`         TEXT           NULL,
  `StateAvg`       VARCHAR(50)    NULL
);
