#! /bin/sh

case $1 in
  csv|list)
    mode=$1
    ;;
  *)
    mode=column
    ;;
esac

SQL="status.sql"
sqlite3 -header -$mode checks.db < $SQL
