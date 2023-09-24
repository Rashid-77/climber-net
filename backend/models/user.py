create_user_table_query = """
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` CHAR(50) NOT NULL,
  `first_name` CHAR(30) NOT NULL,
  `last_name` CHAR(30) NOT NULL,
  `age` SMALLINT NOT NULL,
  `bio` VARCHAR(512) NOT NULL,
  `city` CHAR(50) NOT NULL,
  `country` CHAR(50) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  `disabled` BOOL NOT NULL,
  PRIMARY KEY (id)
);
"""
