"""Phase 0 follow-up: degraded reader ergonomics.

Goal: prove the single-flow workflow:
  PyIceberg.load_table(<fqn>) -> metadata_location
  -> MotherDuck.execute(f"SELECT * FROM iceberg_scan('{loc}')")

If this works cleanly, option A (degraded reader bypassing
catalog ATTACH) is viable as Phase 1.

Also probes: does an inserted row via PyIceberg become visible
to MotherDuck immediately when we follow the freshly-loaded
metadata pointer?
"""
from __future__ import annotations
import os, sys, time
import duckdb
import pyarrow as pa
from dotenv import load_dotenv
from pyiceberg.catalog.rest import RestCatalog

load_dotenv()
ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
BUCKET = os.environ["R2_BUCKET"]
TOKEN = os.environ["R2_TOKEN_VALUE"]
KEY = os.environ["R2_ACCESS_KEY_ID"]
SECRET = os.environ["R2_SECRET_ACCESS_KEY"]
WAREHOUSE = f"{ACCOUNT_ID}_{BUCKET}"
URI = f"https://catalog.cloudflarestorage.com/{ACCOUNT_ID}/{BUCKET}"


def step(label, fn):
    print(f"\n[step] {label}", flush=True)
    try:
        r = fn()
        print(f"[step] OK -> {r!r}", flush=True)
        return r
    except BaseException as e:
        print(f"[step] FAIL: {type(e).__name__}: {e}", flush=True)
        sys.stdout.flush()
        return e


# ---- 1. PyIceberg: resolve current metadata pointer ----
catalog = RestCatalog(name="r2", warehouse=WAREHOUSE, uri=URI, token=TOKEN)
tbl = step("pyiceberg load_table spike.trivial",
           lambda: catalog.load_table("spike.trivial"))
metadata_location = tbl.metadata_location
print(f"[probe] metadata_location={metadata_location}", flush=True)

# ---- 2. MotherDuck: iceberg_scan that pointer ----
conn = duckdb.connect(f"md:?motherduck_token={os.environ['MOTHERDUCK_TOKEN']}")
conn.execute("INSTALL iceberg; LOAD iceberg;")

step("md scan resolved pointer", lambda:
    conn.execute(
        f"SELECT * FROM iceberg_scan('{metadata_location}') ORDER BY id;"
    ).fetchall()
)

# ---- 3. Append fresh rows via PyIceberg, re-resolve, re-scan ----
new_rows = pa.Table.from_pylist([
    {"id": 99, "label": f"diag_{int(time.time())}"},
])
tbl.append(new_rows)
print(f"[probe] appended 1 row via PyIceberg", flush=True)

# Reload to get latest metadata pointer
tbl2 = catalog.load_table("spike.trivial")
new_metadata = tbl2.metadata_location
print(f"[probe] new metadata_location={new_metadata}", flush=True)
print(f"[probe] same pointer? {new_metadata == metadata_location}", flush=True)

step("md scan NEW pointer (sees appended row)", lambda:
    conn.execute(
        f"SELECT id, label FROM iceberg_scan('{new_metadata}') "
        "WHERE id=99 ORDER BY label DESC LIMIT 5;"
    ).fetchall()
)

# ---- 4. Wrap as a MotherDuck view? (will go stale on next append) ----
step("md create temp view over current pointer", lambda:
    conn.execute(
        f"CREATE OR REPLACE TEMP VIEW spike_trivial AS "
        f"SELECT * FROM iceberg_scan('{new_metadata}');"
    )
)
step("md select via view", lambda:
    conn.execute("SELECT count(*) FROM spike_trivial;").fetchone()
)

# ---- 5. Helper: PyIceberg list_tables in catalog ----
step("pyiceberg list_tables in spike", lambda:
    catalog.list_tables("spike")
)
