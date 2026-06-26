import io, os, duckdb, boto3, pandas as pd
from botocore.client import Config
from datasets import load_dataset, Dataset
from huggingface_hub import HfApi

BUCKET = "lakehouse"
USER = HfApi().whoami(token=os.environ["HF_TOKEN"])["name"]

s3 = boto3.client("s3", endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-east-1", config=Config(s3={"addressing_style": "path"}))

con = duckdb.connect()
con.execute(open("sql/00_attach.sql").read())

print("=== PART 1: incremental ingest from Hugging Face into raw ===")
print("raw.coco_annotations rows BEFORE:", con.execute("SELECT count(*) FROM raw.coco_annotations").fetchone()[0])
ds = load_dataset("detection-datasets/coco", split="val", streaming=True)
rows = []
for i, ex in enumerate(ds):
    if i < 30:   continue
    if i >= 40:  break
    image_id = ex["image_id"]
    buf = io.BytesIO(); ex["image"].convert("RGB").save(buf, format="JPEG")
    key = f"assets/coco/{image_id}.jpg"
    s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())
    uri = f"s3://{BUCKET}/{key}"
    objs = ex["objects"]
    for j in range(len(objs["bbox_id"])):
        rows.append({"image_id": image_id, "image_uri": uri, "width": ex["width"],
            "height": ex["height"], "bbox_id": objs["bbox_id"][j],
            "category": objs["category"][j], "bbox": objs["bbox"][j]})
inc = pd.DataFrame(rows)
con.execute("INSERT INTO raw.coco_annotations SELECT * FROM inc")
print("raw.coco_annotations rows AFTER :", con.execute("SELECT count(*) FROM raw.coco_annotations").fetchone()[0])
print("new snapshot:", con.execute("SELECT max(snapshot_id) FROM ducklake_snapshots('lake')").fetchone()[0])

print("\n=== PART 2: push a gold table back to the Hugging Face Hub ===")
gdf = con.execute("SELECT * FROM gold.coco_train").df()
hub_id = f"{USER}/lakehouse-coco-gold"
print(f"pushing gold.coco_train ({len(gdf)} rows) to {hub_id} ...")
Dataset.from_pandas(gdf, preserve_index=False).push_to_hub(hub_id, token=os.environ["HF_TOKEN"])
print(f"\nDONE. Your dataset is live at:\n  https://huggingface.co/datasets/{hub_id}")
