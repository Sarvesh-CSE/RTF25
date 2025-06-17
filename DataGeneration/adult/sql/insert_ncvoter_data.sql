-- sql/insert_voter_data.sql
INSERT INTO `voter_data` (
  `voter_id`, `voter_reg_num`, `name_prefix`, `first_name`, `middle_name`,
  `last_name`, `name_suffix`, `age`, `gender`, `race`,
  `ethnic`, `street_address`, `city`, `state`, `zip_code`,
  `full_phone_num`, `birth_place`, `register_date`, `download_month`
) VALUES (
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s, %s,
  %s, %s, %s, %s
);