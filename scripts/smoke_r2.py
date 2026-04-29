"""Prove R2 credentials reach the configured bucket.

Acceptance criterion 3: boto3 head_bucket succeeds against the R2 endpoint.
Also uploads a one-row Parquet placeholder so the MotherDuck smoke test
has something to read.
"""

import io
import os

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
BUCKET = os.environ["R2_BUCKET"]
ENDPOINT = f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com"
PLACEHOLDER_KEY = "smoke/placeholder.parquet"


def main() -> None:
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT,
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )

    s3.head_bucket(Bucket=BUCKET)
    print(f"OK head_bucket {BUCKET} via {ENDPOINT}")

    table = pa.table({"id": [1], "note": ["dream-job-radar smoke"]})
    buf = io.BytesIO()
    pq.write_table(table, buf)
    s3.put_object(Bucket=BUCKET, Key=PLACEHOLDER_KEY, Body=buf.getvalue())
    print(f"OK put_object s3://{BUCKET}/{PLACEHOLDER_KEY}")


if __name__ == "__main__":
    main()
