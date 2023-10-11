CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` CHAR(50) NOT NULL,
  `first_name` CHAR(50) NOT NULL,
  `last_name` CHAR(50) NOT NULL,
  `age` SMALLINT NOT NULL,
  `bio` VARCHAR(512) NOT NULL,
  `city` CHAR(100) NOT NULL,
  `country` CHAR(100) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  `disabled` BOOL NOT NULL,
  PRIMARY KEY (id)
);