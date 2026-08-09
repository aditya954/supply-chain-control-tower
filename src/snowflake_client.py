"""Snowflake connection helper."""

from __future__ import annotations

from pathlib import Path

import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from src.config import SnowflakeConfig


def load_private_key(key_path: str, passphrase: str) -> bytes:
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


def get_connection(cfg: SnowflakeConfig, schema: str = "AI"):
    if not cfg.account or not cfg.user:
        raise ValueError("SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER must be set in .env")

    key_path = Path(cfg.private_key_path)
    if not key_path.exists():
        raise FileNotFoundError(f"Snowflake private key not found: {key_path}")

    return snowflake.connector.connect(
        account=cfg.account,
        user=cfg.user,
        role=cfg.role,
        warehouse=cfg.warehouse,
        database=cfg.database,
        schema=schema,
        private_key=load_private_key(cfg.private_key_path, cfg.private_key_passphrase),
    )
