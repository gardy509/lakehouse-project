import os, random, duckdb, boto3, pandas as pd
from botocore.client import Config

random.seed(7)
BUCKET = "lakehouse"
CLASSES = ["pedestrian", "car", "van", "truck", "bus", "motor", "bicycle"]
FPS = 30
FRAMES_PER_FRAG = 30
FRAGS_PER_CLIP = 8
clips = ["uav0000013_00000_v", "uav0000073_00600_v", "uav0000099_02109_v"]

s3 = boto3.client("s3", endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name="us-east-1", config=Config(s3={"addressing_style": "path"}))

rows = []
for clip in clips:
    clip_uri = f"s3://{BUCKET}/assets/visdrone/{clip}.mp4"
    for f in range(FRAGS_PER_CLIP):
        start_frame = f * FRAMES_PER_FRAG
        end_frame = start_frame + FRAMES_PER_FRAG - 1
        payload = bytes(random.getrandbits(8) for _ in range(2048))
        key = f"assets/visdrone/{clip}/frag_{f:03d}.bin"
        s3.put_object(Bucket=BUCKET, Key=key, Body=payload)
        rows.append({
            "clip_id": clip,
            "clip_uri": clip_uri,
            "fragment_id": f,
            "fragment_uri": f"s3://{BUCKET}/{key}",
            "start_frame": start_frame,
            "end_frame": end_frame,
            "start_time": round(start_frame / FPS, 3),
            "end_time": round(end_frame / FPS, 3),
            "n_objects": random.choice([2, 3, 5, 8, 12, 18, 25, 33, 40]),
            "classes": random.sample(CLASSES, k=random.randint(1, 4)),
        })

df = pd.DataFrame(rows)
con = duckdb.connect()
con.execute(open("sql/00_attach.sql").read())
con.execute("DROP TABLE IF EXISTS raw.visdrone_fragments")
con.execute("CREATE TABLE raw.visdrone_fragments AS SELECT * FROM df")
print("raw.visdrone_fragments landed:")
print(con.sql("SELECT clip_id, fragment_id, start_frame, end_frame, n_objects, classes FROM raw.visdrone_fragments ORDER BY clip_id, fragment_id LIMIT 10"))
print("\ncounts:")
print(con.sql("SELECT count(*) AS fragments, count(DISTINCT clip_id) AS clips FROM raw.visdrone_fragments"))

print("\n=== VIDEO-FRAGMENT QUERY: busiest fragments (n_objects > 20) ===")
busy = con.execute("SELECT clip_id, fragment_id, fragment_uri, n_objects FROM raw.visdrone_fragments WHERE n_objects > 20 ORDER BY n_objects DESC").fetchall()
print(f"{len(busy)} busy fragments. Fetching ONLY those bytes from RustFS (not whole clips):")
total = 0
for clip_id, frag_id, uri, n in busy:
    key = uri.replace(f"s3://{BUCKET}/", "")
    nbytes = len(s3.get_object(Bucket=BUCKET, Key=key)["Body"].read())
    total += nbytes
    print(f"  {clip_id} frag {frag_id}: {n} objects -> read {nbytes} bytes")
print(f"\nread only {len(busy)} fragments ({total} bytes total) instead of all {len(df)} fragments.")
print("\nlatest snapshot:")
print(con.sql("SELECT max(snapshot_id) AS latest FROM ducklake_snapshots('lake')"))
