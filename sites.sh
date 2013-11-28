OUT=sites.csv
sqlite3 -header -csv checks.db "SELECT * FROM site" > $OUT
cat $OUT
