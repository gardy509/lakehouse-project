import os, glob, boto3
from botocore.client import Config

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    config=Config(s3={"addressing_style": "path"}),
)

bucket = "lakehouse"
deleted = 0
paginator = s3.get_paginator("list_objects_v2")
try:
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            s3.delete_object(Bucket=bucket, Key=obj["Key"])
            deleted += 1
    print(f"emptied {deleted} objects from {bucket}")
except s3.exceptions.NoSuchBucket:
    print(f"{bucket} did not exist")

try:
    s3.create_bucket(Bucket=bucket)
    print(f"created bucket {bucket}")
except Exception:
    print(f"bucket {bucket} already present")

for f in glob.glob("metadata.ducklake*"):
    os.remove(f)
    print(f"removed {f}")

print("reset done")
