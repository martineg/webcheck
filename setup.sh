#! /bin/sh

db=checks.db

if [ ! -f $db ]; then
  echo "Creating checks database"
  sqlite3 $db < schema.sql
fi

echo "Created database - add sites before running checks"
