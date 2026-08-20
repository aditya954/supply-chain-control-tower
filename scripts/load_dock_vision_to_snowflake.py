#!/usr/bin/env python3
"""Load DockVision inspections CSV into Snowflake RAW.DV_LOAD_INSPECTIONS."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "dock_vision" / "inspections.csv"
SNOWFLAKE_DIR = PROJECT_ROOT / "snowflake" / "dock_vision"
DATABASE_NAME = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")

DDL_SCRIPTS = ["01_schemas.sql", "02_raw_tables.sql"]


def load_private_key() -> bytes:
    load_dotenv(PROJECT_ROOT / ".env")
    key_path = os.environ.get(
        "SNOWFLAKE_PRIVATE_KEY_PATH",
        str(Path.home() / ".dbt/snowflake_keys/rsa_key.p8"),
    )
    passphrase = os.environ.get("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", "")
    with open(key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=passphrase.encode() if passphrase else None,
            backend=default_backend(),
        )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_connection():
    load_dotenv(PROJECT_ROOT / ".env")
    return snowflake.connector.connect(
        account=os.environ.get("SNOWFLAKE_ACCOUNT", ""),
        user=os.environ.get("SNOWFLAKE_USER", ""),
        role=os.environ.get("SNOWFLAKE_ROLE", "TRANSFORMER"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "DBT_WH"),
        database=DATABASE_NAME,
        schema="RAW",
        private_key=load_private_key(),
    )


def _strip_sql_comments(sql: str) -> str:
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    return "\n".join(lines)


def _split_statements(sql: str) -> list[str]:
    cleaned = _strip_sql_comments(sql)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


def run_ddl(cursor) -> None:
    for script_name in DDL_SCRIPTS:
        path = SNOWFLAKE_DIR / script_name
        sql = path.read_text(encoding="utf-8")
        for statement in _split_statements(sql):
            cursor.execute(statement)
        print(f"Applied {script_name}")


def main() -> int:
    if not DATA_FILE.exists():
        print(f"Missing data file: {DATA_FILE}")
        print("Run: python3 scripts/generate_dock_vision_sample_data.py")
        return 1

    frame = pd.read_csv(DATA_FILE)
    frame["CAPTURED_AT"] = pd.to_datetime(frame["captured_at"], utc=True, errors="coerce")
    frame["SYNCED_TO_SNOWFLAKE"] = True
    upload = frame.rename(columns={col: col.upper() for col in frame.columns})

    conn = get_connection()
    try:
        cursor = conn.cursor()
        run_ddl(cursor)
        cursor.execute("DELETE FROM RAW.DV_LOAD_INSPECTIONS")
        success, _, row_count, _ = write_pandas(
            conn,
            upload,
            "DV_LOAD_INSPECTIONS",
            database=DATABASE_NAME,
            schema="RAW",
            auto_create_table=False,
            quote_identifiers=False,
        )
        if not success:
            raise RuntimeError("Snowflake write_pandas returned success=False")
        print(f"Loaded {row_count} rows into RAW.DV_LOAD_INSPECTIONS")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
