import duckdb
con = duckdb.connect()
con.execute(open("sql/00_attach.sql").read())
con.execute("DROP TABLE IF EXISTS raw.hello")
con.execute("CREATE TABLE raw.hello AS SELECT 1 AS id, 'world' AS msg")
print("TABLE CONTENTS:")
print(con.sql("SELECT * FROM raw.hello"))
print("SNAPSHOTS:")
try:
    print(con.sql("FROM ducklake_snapshots('lake')"))
except Exception as e:
    print("(snapshot function name differs in this version:", e, ")")
