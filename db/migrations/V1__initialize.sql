CREATE TABLE announcer(
  hook_id VARCHAR(255) PRIMARY KEY NOT NULL,
  token VARCHAR(255) NOT NULL DEFAULT '',
  day INT NOT NULL DEFAULT 0,
  announce_at VARCHAR(10) NOT NULL DEFAULT '21 31',
  announced_today VARCHAR(255) NOT NULL DEFAULT 'no'
);

CREATE TABLE message(
  id SERIAL PRIMARY KEY NOT NULL,
  msg VARCHAR(4000) NOT NULL DEFAULT ''
);

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
