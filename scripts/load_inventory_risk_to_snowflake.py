#!/usr/bin/env python3
"""Load Inventory Risk Assistant CSVs into Snowflake RAW.IR_* tables."""

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
DATA_DIR = PROJECT_ROOT / "data" / "inventory_risk"
SNOWFLAKE_DIR = PROJECT_ROOT / "snowflake" / "inventory_risk"
DATABASE_NAME = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")

TABLE_FILES = {
    "IR_INVENTORY": DATA_DIR / "inventory.csv",
    "IR_SUPPLIERS": DATA_DIR / "suppliers.csv",
    "IR_PURCHASE_ORDERS": DATA_DIR / "purchase_orders.csv",
    "IR_SHIPMENTS": DATA_DIR / "shipments.csv",
    "IR_FORECAST": DATA_DIR / "forecast.csv",
}

DDL_SCRIPTS = ["01_schemas.sql", "02_raw_tables.sql"]


def load_private_key() -> bytes:
    load_dotenv(PROJECT_ROOT / ".env")
    key_path = os.environ.get(
        "SNOWFLAKE_PRIVATE_KEY_PATH",
        "/Users/aditya954/.dbt/snowflake_keys/rsa_key.p8",
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
        account=os.environ.get("SNOWFLAKE_ACCOUNT", "ewefaqm-lr31508"),
        user=os.environ.get("SNOWFLAKE_USER", "ADITYA253032"),
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
        if not path.exists():
            raise FileNotFoundError(f"Missing DDL script: {path}")
        print(f"Executing {script_name}...")
        for statement in _split_statements(path.read_text(encoding="utf-8")):
            cursor.execute(statement)


def prepare_dataframe(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    date_cols = {
        "IR_INVENTORY": ["snapshot_date"],
        "IR_PURCHASE_ORDERS": ["expected_date"],
        "IR_SHIPMENTS": ["shipment_date", "expected_delivery", "actual_delivery"],
        "IR_FORECAST": ["forecast_date"],
    }
    for col in date_cols.get(table_name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    if table_name == "IR_SHIPMENTS" and "actual_delivery" in df.columns:
        df["actual_delivery"] = df["actual_delivery"].where(df["actual_delivery"].notna(), None)
    return df


def load_table(conn, table_name: str, file_path: Path) -> int:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing {file_path}. Run: python3 scripts/generate_inventory_risk_data.py"
        )
    df = prepare_dataframe(table_name, pd.read_csv(file_path))
    success, _nchunks, nrows, _ = write_pandas(
        conn,
        df,
        table_name,
        database=DATABASE_NAME,
        schema="RAW",
        auto_create_table=False,
        overwrite=True,
        quote_identifiers=False,
    )
    if not success:
        raise RuntimeError(f"Failed to load {table_name}")
    print(f"Loaded {table_name}: {nrows:,} rows")
    return nrows


def validate(cursor) -> None:
    print("\n=== Validation ===")
    cursor.execute(
        """
        SELECT table_name, row_count FROM (
          SELECT 'IR_INVENTORY' AS table_name, COUNT(*) AS row_count FROM IR_INVENTORY
          UNION ALL SELECT 'IR_SUPPLIERS', COUNT(*) FROM IR_SUPPLIERS
          UNION ALL SELECT 'IR_PURCHASE_ORDERS', COUNT(*) FROM IR_PURCHASE_ORDERS
          UNION ALL SELECT 'IR_SHIPMENTS', COUNT(*) FROM IR_SHIPMENTS
          UNION ALL SELECT 'IR_FORECAST', COUNT(*) FROM IR_FORECAST
        ) ORDER BY table_name
        """
    )
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,} rows")

    cursor.execute(
        """
        SELECT product_name, warehouse, stock_qty, daily_demand,
               ROUND(stock_qty / NULLIF(daily_demand, 0), 2) AS days_of_supply
        FROM IR_INVENTORY WHERE product_id = 'P001'
        """
    )
    coconut = cursor.fetchone()
    if coconut:
        print(
            f"\n  Demo — {coconut[0]} @ {coconut[1]}: "
            f"stock={coconut[2]}, demand={coconut[3]}, DOS={coconut[4]}"
        )


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        run_ddl(cursor)
        cursor.execute(f"USE DATABASE {DATABASE_NAME}")
        cursor.execute("USE SCHEMA RAW")
        total = 0
        for table_name, file_path in TABLE_FILES.items():
            print(f"Loading {table_name}...")
            total += load_table(conn, table_name, file_path)
        print(f"\nTotal rows loaded: {total:,}")
        validate(cursor)
        print(f"\nAll Inventory Risk tables loaded into {DATABASE_NAME}.RAW")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
