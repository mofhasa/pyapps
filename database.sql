DROP TABLE `Positions`;
DROP TABLE `Companies`;
DROP TABLE `Recruiters`;

CREATE TABLE IF NOT EXISTS `Positions` (
  `company_id` integer NOT NULL,
  `title` text NOT NULL,
  `link` text,
  `keywords` text,
  FOREIGN KEY(company_id) REFERENCES Companies(id),
  PRIMARY KEY (company_id, title)
);

CREATE TABLE IF NOT EXISTS `Companies` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
  `name` text NOT NULL
);


CREATE TABLE IF NOT EXISTS `Recruiters` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
  `name` text NOT NULL,
  `company` integer NOT NULL,
  `email` text NOT NULL,
  `domain` text NOT NULL,
  `last_communicated` date,
  `last_heard_back` date,
  FOREIGN KEY(company) REFERENCES Companies(id)
) ;
