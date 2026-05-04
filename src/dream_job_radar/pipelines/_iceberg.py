"""Shared Iceberg REST catalog factory for R2 Data Catalog.

Mirrors `_r2.py` shape: one function returning a configured
client. Entrypoints handle dotenv loading; this module reads
env vars directly.

R2 Data Catalog speaks the Iceberg REST spec. Warehouse and URI
are derived from the account id and bucket name; the auth token
is the R2 API token (`R2_TOKEN_VALUE`) with Admin Read & Write
permissions covering both R2 Storage and R2 Data Catalog.
"""

from __future__ import annotations

import os

from pyiceberg.catalog.rest import RestCatalog


def iceberg_catalog() -> RestCatalog:
    account_id = os.environ["R2_ACCOUNT_ID"]
    bucket = os.environ["R2_BUCKET"]
    return RestCatalog(
        name="r2",
        warehouse=f"{account_id}_{bucket}",
        uri=f"https://catalog.cloudflarestorage.com/{account_id}/{bucket}",
        token=os.environ["R2_TOKEN_VALUE"],
    )
