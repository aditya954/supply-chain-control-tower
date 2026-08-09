"""Embedding providers and incremental sync pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config import AppConfig, EmbeddingConfig, load_config
from src.logging_config import configure_logging, new_request_id
from src.snowflake_client import get_connection

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DDL_PATH = PROJECT_ROOT / "snowflake" / "inventory_risk" / "04_ai_vector_table.sql"


@dataclass
class ContextDocument:
    document_id: str
    product_id: str
    warehouse: str
    risk_level: str
    document_text: str
    document_hash: str


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class CortexEmbeddingProvider(EmbeddingProvider):
    def __init__(self, cursor: Any, model: str) -> None:
        self.cursor = cursor
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            self.cursor.execute(
                "SELECT snowflake.cortex.embed_text(%s, %s) AS embedding",
                (self.model, text),
            )
            row = self.cursor.fetchone()
            if row is None or row[0] is None:
                raise RuntimeError("Cortex returned null embedding")
            vectors.append(_parse_embedding(row[0]))
        return vectors


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "Install sentence-transformers for local embeddings: "
                "pip install sentence-transformers"
            ) from exc
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()


def _parse_embedding(value: Any) -> list[float]:
    if isinstance(value, list):
        return [float(x) for x in value]
    if isinstance(value, str):
        return [float(x) for x in json.loads(value)]
    return [float(x) for x in value]


def _strip_sql_comments(sql: str) -> str:
    lines = [line for line in sql.splitlines() if not line.strip().startswith("--")]
    return "\n".join(lines)


def _split_statements(sql: str) -> list[str]:
    cleaned = _strip_sql_comments(sql)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


def ensure_vector_table(cursor: Any) -> None:
    if not DDL_PATH.exists():
        raise FileNotFoundError(f"Missing DDL: {DDL_PATH}")
    for statement in _split_statements(DDL_PATH.read_text(encoding="utf-8")):
        cursor.execute(statement)


def fetch_context_documents(cursor: Any, table: str) -> list[ContextDocument]:
    cursor.execute(
        f"""
        SELECT
            document_id,
            product_id,
            warehouse,
            risk_level,
            document_text,
            document_hash
        FROM {table}
        """
    )
    return [
        ContextDocument(
            document_id=row[0],
            product_id=row[1],
            warehouse=row[2],
            risk_level=row[3],
            document_text=row[4],
            document_hash=row[5],
        )
        for row in cursor.fetchall()
    ]


def fetch_existing_hashes(cursor: Any, table: str) -> dict[str, str]:
    cursor.execute(f"SELECT document_id, document_hash FROM {table}")
    return {row[0]: row[1] for row in cursor.fetchall()}


def documents_needing_embedding(
    documents: list[ContextDocument],
    existing_hashes: dict[str, str],
) -> list[ContextDocument]:
    return [
        doc
        for doc in documents
        if existing_hashes.get(doc.document_id) != doc.document_hash
    ]


def build_provider(cfg: EmbeddingConfig, cursor: Any) -> EmbeddingProvider:
    if cfg.provider == "cortex":
        return CortexEmbeddingProvider(cursor, cfg.model)
    if cfg.provider == "local":
        return LocalEmbeddingProvider(cfg.model)
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {cfg.provider}")


def format_vector_sql(vector: list[float], dimension: int) -> str:
    """Snowflake vector literal: [1.0,2.0]::VECTOR(FLOAT, n)."""
    literal = "[" + ",".join(str(float(v)) for v in vector) + "]"
    return f"{literal}::VECTOR(FLOAT, {dimension})"


def upsert_embeddings(
    cursor: Any,
    cfg: EmbeddingConfig,
    documents: list[ContextDocument],
    vectors: list[list[float]],
) -> int:
    if len(documents) != len(vectors):
        raise ValueError("documents and vectors length mismatch")

    for doc, vector in zip(documents, vectors):
        vector_sql = format_vector_sql(vector, cfg.dimension)
        cursor.execute(
            f"""
            MERGE INTO {cfg.embeddings_table} AS target
            USING (
                SELECT
                    %s AS document_id,
                    %s AS product_id,
                    %s AS warehouse,
                    %s AS risk_level,
                    %s AS document_text,
                    {vector_sql} AS embedding,
                    %s AS embedding_model,
                    %s AS embedding_version,
                    %s AS document_hash
            ) AS source
            ON target.document_id = source.document_id
            WHEN MATCHED THEN UPDATE SET
                product_id = source.product_id,
                warehouse = source.warehouse,
                risk_level = source.risk_level,
                document_text = source.document_text,
                embedding = source.embedding,
                embedding_model = source.embedding_model,
                embedding_version = source.embedding_version,
                document_hash = source.document_hash,
                updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN INSERT (
                document_id, product_id, warehouse, risk_level, document_text,
                embedding, embedding_model, embedding_version, document_hash,
                created_at, updated_at
            ) VALUES (
                source.document_id, source.product_id, source.warehouse,
                source.risk_level, source.document_text, source.embedding,
                source.embedding_model, source.embedding_version, source.document_hash,
                CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
            )
            """,
            (
                doc.document_id,
                doc.product_id,
                doc.warehouse,
                doc.risk_level,
                doc.document_text,
                cfg.model,
                cfg.version,
                doc.document_hash,
            ),
        )
    return len(documents)


class EmbeddingPipeline:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()

    def sync(self) -> dict[str, int]:
        start = time.perf_counter()
        cfg = self.config
        db = cfg.snowflake.database
        context_table = f"{db}.AI.{cfg.embedding.context_table}"
        embeddings_table = f"{db}.AI.{cfg.embedding.embeddings_table}"

        conn = get_connection(cfg.snowflake, schema="AI")
        cursor = conn.cursor()
        try:
            ensure_vector_table(cursor)
            cursor.execute(f"USE DATABASE {db}")
            cursor.execute("USE SCHEMA AI")

            all_docs = fetch_context_documents(cursor, context_table)
            existing = fetch_existing_hashes(cursor, embeddings_table)
            to_embed = documents_needing_embedding(all_docs, existing)

            logger.info(
                "embedding_sync_start total=%s existing=%s to_embed=%s",
                len(all_docs),
                len(existing),
                len(to_embed),
            )

            if not to_embed:
                elapsed = time.perf_counter() - start
                logger.info("embedding_sync_skip reason=no_changes elapsed=%.2fs", elapsed)
                return {
                    "total_documents": len(all_docs),
                    "embedded": 0,
                    "skipped": len(all_docs),
                }

            provider = build_provider(cfg.embedding, cursor)
            vectors = provider.embed([doc.document_text for doc in to_embed])
            embedded = upsert_embeddings(cursor, cfg.embedding, to_embed, vectors)
            conn.commit()

            elapsed = time.perf_counter() - start
            logger.info(
                "embedding_sync_complete embedded=%s elapsed=%.2fs model=%s",
                embedded,
                elapsed,
                cfg.embedding.model,
            )
            return {
                "total_documents": len(all_docs),
                "embedded": embedded,
                "skipped": len(all_docs) - embedded,
            }
        finally:
            cursor.close()
            conn.close()


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    new_request_id()
    parser = argparse.ArgumentParser(description="Sync document embeddings to Snowflake")
    parser.parse_args(argv)

    try:
        result = EmbeddingPipeline().sync()
        print(
            f"Embedding sync complete: embedded={result['embedded']}, "
            f"skipped={result['skipped']}, total={result['total_documents']}"
        )
        return 0
    except Exception:
        logger.exception("embedding_sync_failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
