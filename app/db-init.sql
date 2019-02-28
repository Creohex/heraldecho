CREATE DATABASE IF NOT EXISTS deeprock;

USE deeprock;

DROP TABLE IF EXISTS announcer;
DROP TABLE IF EXISTS messages;

CREATE TABLE announcer(
  hook_id VARCHAR(255) NOT NULL,
  token VARCHAR(255) NOT NULL DEFAULT '',
  day INT NOT NULL DEFAULT 0,
  announced_today VARCHAR(255) NOT NULL DEFAULT 'no',

  PRIMARY KEY (hook_id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;

CREATE TABLE message(
  id INT NOT NULL AUTO_INCREMENT,
  msg VARCHAR(4000) NOT NULL DEFAULT '',

  PRIMARY KEY (id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci ENGINE=InnoDB;

INSERT INTO message (msg) VALUES
('Get on board the Drop Pod team - mission is ready!'),
('Drop Pod is ready - time to leave!'),
('Your mission is ready, the pod is prepped - get on board the Drop Pod!'),
('Drop Pod has cleared warm-up. Time to get to work, team.'),
('Orders from management: Stop dancing and get to it!'),
('You boys better be better miners than you are dancers.'),
('You know... You are not being paid by the hour! Get to work!'),
('Classy moves, team. Now quit it!'),
('This area is under construction, please turn around!'),
('Hold on to your butts, commencing gravity calibration.');

