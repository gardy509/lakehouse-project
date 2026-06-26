import duckdb
con = duckdb.connect()
con.execute(open("sql/00_attach.sql").read())
print(con.sql("FROM ducklake_snapshots('lake')"))
