import duckdb
con = duckdb.connect()
con.execute(open("sql/00_attach.sql").read())

def latest():
    return con.execute("SELECT max(snapshot_id) FROM ducklake_snapshots('lake')").fetchone()[0]

print("=== 1. starting table ===")
print(con.sql("SELECT * FROM raw.hello ORDER BY id"))

con.execute("INSERT INTO raw.hello VALUES (2, 'lakehouse'), (3, 'rocks')")
good = latest()
print(f"\n=== 2. added rows -> snapshot {good} (our GOOD version) ===")
print(con.sql("SELECT * FROM raw.hello ORDER BY id"))

con.execute("UPDATE raw.hello SET msg = 'CORRUPTED'")
bad = latest()
print(f"\n=== 3. a BAD update -> snapshot {bad} (data ruined) ===")
print(con.sql("SELECT * FROM raw.hello ORDER BY id"))

print(f"\n=== 4. TIME TRAVEL: read version {good} without changing anything ===")
print(con.sql(f"SELECT * FROM raw.hello AT (VERSION => {good}) ORDER BY id"))

print(f"\n=== 5. ROLLBACK to version {good} (delete + re-insert the good rows) ===")
con.execute(f"CREATE OR REPLACE TEMP TABLE good_rows AS SELECT * FROM raw.hello AT (VERSION => {good})")
con.execute("DELETE FROM raw.hello")
con.execute("INSERT INTO raw.hello SELECT * FROM good_rows")
print(con.sql("SELECT * FROM raw.hello ORDER BY id"))

print("\n=== 6. full snapshot history ===")
print(con.sql("SELECT snapshot_id, snapshot_time, changes FROM ducklake_snapshots('lake') ORDER BY snapshot_id"))
