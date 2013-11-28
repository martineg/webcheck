CREATE TABLE site (
    site_id integer primary key autoincrement,
    hostname text, uri text);
CREATE TABLE webcheck (
check_id integer primary key,
timestamp integer,
site text,
duration real,
result text,
size integer);
