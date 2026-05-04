import os, duckdb
from dotenv import load_dotenv
load_dotenv()
ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
BUCKET = os.environ["R2_BUCKET"]
METADATA = (
    f"s3://{BUCKET}/__r2_data_catalog/"
    "019df0ea-14be-7080-885c-7d01165fec42/"
    "019df0ea-174e-7921-8878-4ac7334bcece/metadata/"
    "00002-019df0ea-75ba-7f63-b04a-1a88438388fc.gz.metadata.json"
)
conn = duckdb.connect(f"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}")
conn.execute("INSTALL iceberg; LOAD iceberg;")
conn.execute("SET unsafe_enable_version_guessing = true;")
conn.execute(f"""
CREATE OR REPLACE SECRET r2_s3_md (
  TYPE S3, KEY_ID '{os.environ["R2_ACCESS_KEY_ID"]}',
  SECRET '{os.environ["R2_SECRET_ACCESS_KEY"]}',
  ENDPOINT '{ACCOUNT_ID}.r2.cloudflarestorage.com',
  REGION 'auto', URL_STYLE 'path', SCOPE 's3://{BUCKET}'
);
""")
print("[md] iceberg_scan direct...")
try:
    rows = conn.execute(f"SELECT * FROM iceberg_scan('{METADATA}') ORDER BY id;").fetchall()
    print(f"[md] OK rows={rows}")
except BaseException as e:
    print(f"[md] FAIL {type(e).__name__}: {e}")
