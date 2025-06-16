-- MySQL/MariaDB format parameters
-- sql/insert_airport_data.sql
INSERT INTO airports (
    id, ident, type, name, latitude_deg, longitude_deg, elevation_ft,
    continent, iso_country, iso_region, municipality, scheduled_service,
    gps_code, iata_code, local_code, home_link, wikipedia_link, keywords
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
);