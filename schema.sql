PRAGMA foreign_keys = ON;
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    department TEXT NOT NULL,
    account_type TEXT NOT NULL CHECK(account_type IN ('human', 'service'))
);
CREATE TABLE auth_events (
    event_id TEXT PRIMARY KEY,
    event_time INTEGER NOT NULL CHECK(typeof(event_time) = 'integer'),
    user_id TEXT NOT NULL REFERENCES users(user_id),
    src_ip TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK(outcome IN ('failure', 'success'))
);
CREATE TABLE access_events (
    access_id TEXT PRIMARY KEY,
    event_time INTEGER NOT NULL CHECK(typeof(event_time) = 'integer'),
    user_id TEXT NOT NULL REFERENCES users(user_id),
    src_ip TEXT NOT NULL,
    resource TEXT NOT NULL,
    bytes_sent INTEGER NOT NULL CHECK(typeof(bytes_sent) = 'integer' AND bytes_sent >= 0)
);
CREATE INDEX auth_pair_time ON auth_events(src_ip, user_id, event_time);
CREATE INDEX auth_user_time ON auth_events(user_id, event_time);
CREATE INDEX access_pair_time ON access_events(user_id, src_ip, event_time);
