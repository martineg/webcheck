#! /bin/sh

SQL="status.sql"
sqlite3 -column -header checks.db < $SQL
