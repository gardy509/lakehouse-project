import io, os, duckdb, boto3, pandas as pd
from botocore.client import Config
from datasets import load_dataset

N = 30
BUCKET = "lakehouse"

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-east-1",
    config=Config(s3={"addressing_style": "path"}),
)

print(f"streaming {N} COCO images, uploading bytes to RustFS, keeping only URIs+metadata...")
ds = load_dataset("detection-datasets/coco", split="val", streaming=True)

rows = []
for i, ex in enumerate(ds):
    if i >= N:
        break
    image_id = ex["image_id"]
    buf = io.BytesIO()
    ex["image"].convert("RGB").save(buf, format="JPEG")
    key = f"assets/coco/{image_id}.jpg"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())
    uri = f"s3://{BUCKET}/{key}"
    objs = ex["objects"]
    for j in range(len(objs["bbox_id"])):
        rows.append({
            "image_id": image_id,
            "image_uri": uri,
            "width": ex["width"],
            "height": ex["height"],
            "bbox_id": objs["bbox_id"][j],
            "category": objs["category"][j],
            "bbox": objs["bbox"][j],
        })
    print(f"  uploaded image {image_id} ({len(objs['bbox_id'])} objects)")

df = pd.DataFrame(rows)
print(f"\nbuilt {len(df)} annotation rows from {N} images")

con = duckdb.connect()
con.execute(open("sql/00_attach.sql").read())
con.execute("DROP TABLE IF EXISTS raw.coco_annotations")
con.execute("CREATE TABLE raw.coco_annotations AS SELECT * FROM df")
print("\nraw.coco_annotations landed. sample:")
print(con.sql("SELECT image_id, image_uri, category, bbox FROM raw.coco_annotations LIMIT 5"))
print("\ncounts:")
print(con.sql("SELECT count(*) AS annotations, count(DISTINCT image_id) AS images FROM raw.coco_annotations"))
print("\nlatest snapshot:")
print(con.sql("SELECT max(snapshot_id) AS latest FROM ducklake_snapshots('lake')"))
