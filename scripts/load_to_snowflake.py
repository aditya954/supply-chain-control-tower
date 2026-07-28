#!/usr/bin/env python3
"""Load sample CSV files into Snowflake RAW schema."""

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
SAMPLE_DATA_DIR = PROJECT_ROOT / "sample_data"
DATABASE_NAME = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")

TABLE_FILES = {
    "supplier": SAMPLE_DATA_DIR / "master" / "supplier.csv",
    "material": SAMPLE_DATA_DIR / "master" / "material.csv",
    "plant": SAMPLE_DATA_DIR / "master" / "plant.csv",
    "warehouse": SAMPLE_DATA_DIR / "master" / "warehouse.csv",
    "machine": SAMPLE_DATA_DIR / "master" / "machine.csv",
    "carrier": SAMPLE_DATA_DIR / "master" / "carrier.csv",
    "customer": SAMPLE_DATA_DIR / "master" / "customer.csv",
    "employee": SAMPLE_DATA_DIR / "master" / "employee.csv",
    "calendar": SAMPLE_DATA_DIR / "master" / "calendar.csv",
    "purchase_orders": SAMPLE_DATA_DIR / "transactional" / "purchase_orders.csv",
    "purchase_order_lines": SAMPLE_DATA_DIR / "transactional" / "purchase_order_lines.csv",
    "inventory": SAMPLE_DATA_DIR / "transactional" / "inventory.csv",
    "inventory_transactions": SAMPLE_DATA_DIR / "transactional" / "inventory_transactions.csv",
    "production_orders": SAMPLE_DATA_DIR / "transactional" / "production_orders.csv",
    "production_transactions": SAMPLE_DATA_DIR / "transactional" / "production_transactions.csv",
    "machine_sensor_readings": SAMPLE_DATA_DIR / "transactional" / "machine_sensor_readings.csv",
    "shipments": SAMPLE_DATA_DIR / "transactional" / "shipments.csv",
    "shipment_tracking": SAMPLE_DATA_DIR / "transactional" / "shipment_tracking.csv",
    "sales_orders": SAMPLE_DATA_DIR / "transactional" / "sales_orders.csv",
    "sales_order_lines": SAMPLE_DATA_DIR / "transactional" / "sales_order_lines.csv",
    "quality_inspection": SAMPLE_DATA_DIR / "transactional" / "quality_inspection.csv",
    "defects": SAMPLE_DATA_DIR / "transactional" / "defects.csv",
    "returns": SAMPLE_DATA_DIR / "transactional" / "returns.csv",
    "warranty_claims": SAMPLE_DATA_DIR / "transactional" / "warranty_claims.csv",
    "supplier_deliveries": SAMPLE_DATA_DIR / "transactional" / "supplier_deliveries.csv",
}


def load_private_key() -> bytes:
    load_dotenv(PROJECT_ROOT / ".env")
    key_path = os.environ.get("SNOWFLAKE_PRIVATE_KEY_PATH") or "/Users/aditya954/.dbt/snowflake_keys/rsa_key.p8"
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
    db = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")
    return snowflake.connector.connect(
        account=os.environ.get("SNOWFLAKE_ACCOUNT", "ewefaqm-lr31508"),
        user=os.environ.get("SNOWFLAKE_USER", "ADITYA253032"),
        role=os.environ.get("SNOWFLAKE_ROLE", "TRANSFORMER"),
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE", "DBT_WH"),
        database=db,
        schema="RAW",
        private_key=load_private_key(),
    )


def setup_database(cursor) -> None:
    db = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")
    cursor.execute(f"USE DATABASE {db}")
    for schema in ("RAW", "STAGING", "INTERMEDIATE", "MART"):
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {db}.{schema}")
    cursor.execute(f"USE SCHEMA {db}.RAW")


def load_table(conn, table_name: str, file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    db = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")
    df = pd.read_csv(file_path)
    success, nchunks, nrows, _ = write_pandas(
        conn,
        df,
        table_name.upper(),
        database=db,
        schema="RAW",
        auto_create_table=True,
        overwrite=True,
        quote_identifiers=False,
    )
    if not success:
        raise RuntimeError(f"Failed to load {table_name}")
    print(f"Loaded {table_name.upper()}: {nrows:,} rows ({nchunks} chunks)")


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    db = os.environ.get("SNOWFLAKE_DATABASE", "ANALYTICS")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        setup_database(cursor)
        for table_name, file_path in TABLE_FILES.items():
            print(f"Loading {table_name}...")
            load_table(conn, table_name, file_path)
        print(f"All tables loaded successfully into {db}.RAW")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
