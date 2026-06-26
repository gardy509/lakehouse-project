import duckdb
con = duckdb.connect()
con.execute(open("sql/00_attach.sql").read())

print("running raw -> silver (clean, type, dedup, + schema evolution)...")
con.execute(open("sql/20_silver.sql").read())
print("running silver -> gold (ML-ready)...")
con.execute(open("sql/30_gold.sql").read())

print("\n=== layer row counts ===")
print(con.sql("""
SELECT 'raw.coco_annotations' AS tbl, count(*) AS rows FROM raw.coco_annotations
UNION ALL SELECT 'raw.visdrone_fragments', count(*) FROM raw.visdrone_fragments
UNION ALL SELECT 'silver.coco', count(*) FROM silver.coco
UNION ALL SELECT 'silver.visdrone', count(*) FROM silver.visdrone
UNION ALL SELECT 'gold.coco_train', count(*) FROM gold.coco_train
UNION ALL SELECT 'gold.visdrone_train', count(*) FROM gold.visdrone_train
ORDER BY tbl
"""))
print("\n=== silver.coco (new bbox_area column = the schema evolution) ===")
print(con.sql("SELECT image_id, category_id, bbox, bbox_area FROM silver.coco LIMIT 5"))
print("\n=== gold.coco_train (image-uri + label + split) ===")
print(con.sql("SELECT * FROM gold.coco_train LIMIT 5"))
print("\n=== gold.visdrone_train ===")
print(con.sql("SELECT fragment_uri, n_objects, is_busy, split FROM gold.visdrone_train LIMIT 5"))
print("\n=== snapshots (watch schema_version bump for ADD COLUMN) ===")
print(con.sql("SELECT snapshot_id, schema_version, changes FROM ducklake_snapshots('lake') ORDER BY snapshot_id DESC LIMIT 8"))
