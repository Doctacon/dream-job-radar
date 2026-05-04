"""Phase 0 spike: PyIceberg ↔ R2 Data Catalog.

Goal: prove a trivial Iceberg table can be created and read against
the R2 Data Catalog enabled on bucket `pipelines`.

Run: `uv run python .loom/evidence/lakehouse-iceberg-spike/spike_pyiceberg.py`

Reads R2 + Cloudflare creds from .env via python-dotenv.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
import pyarrow as pa
from pyiceberg.catalog.rest import RestCatalog
from pyiceberg.exceptions import NoSuchTableError

load_dotenv()

ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
BUCKET = os.environ["R2_BUCKET"]
TOKEN = os.environ["R2_TOKEN_VALUE"]

WAREHOUSE = f"{ACCOUNT_ID}_{BUCKET}"
URI = f"https://catalog.cloudflarestorage.com/{ACCOUNT_ID}/{BUCKET}"

NS = "spike"
TABLE = "trivial"
FQ = f"{NS}.{TABLE}"


def main() -> None:
    print(f"[probe] warehouse={WAREHOUSE}")
    print(f"[probe] uri={URI}")

    catalog = RestCatalog(
        name="r2_spike",
        warehouse=WAREHOUSE,
        uri=URI,
        token=TOKEN,
    )

    print(f"[probe] catalog={catalog!r}")

    print("[probe] listing namespaces...")
    namespaces = catalog.list_namespaces()
    print(f"[probe] namespaces={namespaces}")

    if (NS,) not in namespaces:
        print(f"[probe] creating namespace {NS}")
        catalog.create_namespace(NS)
    else:
        print(f"[probe] namespace {NS} exists")

    rows = pa.Table.from_pylist(
        [
            {"id": 1, "label": "alpha"},
            {"id": 2, "label": "beta"},
            {"id": 3, "label": "gamma"},
        ]
    )

    try:
        tbl = catalog.load_table(FQ)
        print(f"[probe] table {FQ} already exists; appending")
    except NoSuchTableError:
        print(f"[probe] creating table {FQ}")
        tbl = catalog.create_table(FQ, schema=rows.schema)

    tbl.append(rows)
    print("[probe] appended 3 rows")

    out = tbl.scan().to_arrow()
    print(f"[probe] scan rows={out.num_rows}")
    for batch in out.to_batches():
        for row in batch.to_pylist():
            print(f"[probe]   {row}")

    snapshots = list(tbl.metadata.snapshots)
    print(f"[probe] snapshots={len(snapshots)}")
    if snapshots:
        latest = snapshots[-1]
        print(f"[probe] latest_snapshot_id={latest.snapshot_id}")
        print(f"[probe] manifest_list={latest.manifest_list}")

    print(f"[probe] metadata_location={tbl.metadata_location}")


if __name__ == "__main__":
    main()
