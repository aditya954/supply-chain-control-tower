#!/usr/bin/env python3
"""Load AI Control Tower CSV files from data/ into Snowflake RAW.CT_* tables."""

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
DATA_DIR = PROJECT_ROOT / "data"
SNOWFLAKE_DIR = PROJECT_ROOT / "snowflake"
DATABASE_NAME = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")

TABLE_FILES = {
    "CT_PRODUCTS": DATA_DIR / "products.csv",
    "CT_WAREHOUSES": DATA_DIR / "warehouses.csv",
    "CT_SUPPLIERS": DATA_DIR / "suppliers.csv",
    "CT_INVENTORY": DATA_DIR / "inventory.csv",
    "CT_DEMAND": DATA_DIR / "demand.csv",
    "CT_PURCHASE_ORDERS": DATA_DIR / "purchase_orders.csv",
    "CT_SHIPMENTS": DATA_DIR / "shipments.csv",
    "CT_SALES_ORDERS": DATA_DIR / "sales_orders.csv",
}

DDL_SCRIPTS = [
    "01_database.sql",
    "02_schemas.sql",
    "03_raw_tables.sql",
    "04_stages.sql",
]


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


def run_ddl(cursor) -> None:
    for script_name in DDL_SCRIPTS:
        path = SNOWFLAKE_DIR / script_name
        if not path.exists():
            raise FileNotFoundError(f"Missing DDL script: {path}")
        sql = path.read_text(encoding="utf-8")
        print(f"Executing {script_name}...")
        for statement in _split_statements(sql):
            if statement.strip():
                cursor.execute(statement)


def _strip_sql_comments(sql: str) -> str:
    lines = []
    for line in sql.splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    return "\n".join(lines)


def _split_statements(sql: str) -> list[str]:
    """Split SQL file on semicolons, skipping empty fragments."""
    cleaned = _strip_sql_comments(sql)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


def prepare_dataframe(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if table_name == "CT_DEMAND" and "actual_demand" in df.columns:
        df["actual_demand"] = pd.to_numeric(df["actual_demand"], errors="coerce")
    date_cols = {
        "CT_INVENTORY": ["snapshot_date"],
        "CT_DEMAND": ["date"],
        "CT_PURCHASE_ORDERS": ["order_date", "expected_date", "actual_date"],
        "CT_SHIPMENTS": ["ship_date", "expected_delivery", "actual_delivery"],
        "CT_SALES_ORDERS": ["promised_date", "delivery_date"],
    }
    for col in date_cols.get(table_name, []):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df


def load_table(conn, table_name: str, file_path: Path) -> int:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing {file_path}. Run: python3 scripts/generate_control_tower_data.py"
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
          SELECT 'CT_PRODUCTS' AS table_name, COUNT(*) AS row_count FROM CT_PRODUCTS
          UNION ALL SELECT 'CT_WAREHOUSES', COUNT(*) FROM CT_WAREHOUSES
          UNION ALL SELECT 'CT_SUPPLIERS', COUNT(*) FROM CT_SUPPLIERS
          UNION ALL SELECT 'CT_INVENTORY', COUNT(*) FROM CT_INVENTORY
          UNION ALL SELECT 'CT_DEMAND', COUNT(*) FROM CT_DEMAND
          UNION ALL SELECT 'CT_PURCHASE_ORDERS', COUNT(*) FROM CT_PURCHASE_ORDERS
          UNION ALL SELECT 'CT_SHIPMENTS', COUNT(*) FROM CT_SHIPMENTS
          UNION ALL SELECT 'CT_SALES_ORDERS', COUNT(*) FROM CT_SALES_ORDERS
        ) ORDER BY table_name
        """
    )
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,} rows")

    cursor.execute(
        """
        SELECT p.product_name, w.warehouse_name, i.available_qty, i.stock_qty
        FROM CT_INVENTORY i
        JOIN CT_PRODUCTS p ON i.product_id = p.product_id
        JOIN CT_WAREHOUSES w ON i.warehouse_id = w.warehouse_id
        WHERE p.product_id = 'P001' AND w.warehouse_id = 'W01'
        """
    )
    coconut = cursor.fetchone()
    if coconut:
        print(f"\n  Critical scenario — {coconut[0]} @ {coconut[1]}: "
              f"available={coconut[2]}, stock={coconut[3]}")
    else:
        print("\n  WARNING: Coconut/London scenario row not found")


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
        print(f"\nAll Control Tower tables loaded into {DATABASE_NAME}.RAW")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
