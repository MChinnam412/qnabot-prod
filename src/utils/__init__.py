"""
creating mysql table;
CREATE TABLE chat_bot(sessionId VARCHAR(255) PRIMARY KEY,
start_timestamp timestamp default current_timestamp not null,
update_timestamp timestamp default current_timestamp not null,
conversation BLOB(65534));
"""