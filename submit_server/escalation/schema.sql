DROP TABLE IF EXISTS submission;
DROP TABLE IF EXISTS cranks;

CREATE TABLE submission (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  expname TEXT NOT NULL,  
  crank TEXT NOT NULL,  
  filename TEXT NOT NULL,
  notes TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE cranks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  crank TEXT NOT NULL,
  stateset TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO cranks (crank,stateset) VALUES ("0001", "abc123");
INSERT INTO cranks (crank,stateset) VALUES ("0002", "123abc");

INSERT into submission (username, expname, crank, filename, notes) VALUES ("snovot","first","0001","abc.csv","test test");
INSERT into submission (username, expname, crank, filename, notes) VALUES ("snovot","second","0001","abc1.csv","test test");
INSERT into submission (username, expname, crank, filename, notes) VALUES ("snovot","third","0002","abc2.csv","test test");
INSERT into submission (username, expname, crank, filename, notes) VALUES ("snovot","fourth","0002","abc3.csv","test test");
