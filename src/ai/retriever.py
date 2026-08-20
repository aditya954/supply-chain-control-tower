"""Vector retrieval over Snowflake document embeddings."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Any

from src.ai.embeddings import build_provider, format_vector_sql
from src.config import AppConfig, load_config
from src.logging_config import configure_logging, new_request_id
from src.snowflake_client import get_connection

logger = logging.getLogger(__name__)


@dataclass
class RetrievalFilters:
    risk_level: str | None = None
    product_id: str | None = None
    warehouse: str | None = None
    keyword: str | None = None


@dataclass
class RetrievedDocument:
    document_id: str
    product_id: str
    warehouse: str | None
    risk_level: str | None
    document_text: str
    document_hash: str
    similarity_score: float
    embedding_model: str
    metadata: dict[str, str] = field(default_factory=dict)


def build_where_clause(filters: RetrievalFilters | None) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []

    if not filters:
        return "", params

    if filters.risk_level:
        clauses.append("risk_level = %s")
        params.append(filters.risk_level.upper())
    if filters.product_id:
        clauses.append("product_id = %s")
        params.append(filters.product_id.upper())
    if filters.warehouse:
        clauses.append("warehouse = %s")
        params.append(filters.warehouse.upper())
    if filters.keyword:
        clauses.append("document_text ILIKE %s")
        params.append(f"%{filters.keyword}%")

    if not clauses:
        return "", params
    return "WHERE " + " AND ".join(clauses), params


def infer_filters_from_query(query: str) -> RetrievalFilters:
    """Lightweight metadata hints from natural-language questions."""
    q = query.lower()
    filters = RetrievalFilters()

    if "critical" in q:
        filters.risk_level = "CRITICAL"
    elif "high risk" in q or "high-risk" in q:
        filters.risk_level = "HIGH"

    product_aliases = {
        "coconut body wash": "P001",
        "baby formula": "P002",
        "frozen pizza": "P003",
    }
    for alias, product_id in product_aliases.items():
        if alias in q:
            filters.product_id = product_id
            break

    if "london" in q:
        filters.warehouse = "LON"
    elif "new york" in q:
        filters.warehouse = "NYC"

    return filters


class SupplyChainRetriever:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: RetrievalFilters | None = None,
        min_similarity: float = 0.0,
        auto_filter: bool = True,
    ) -> list[RetrievedDocument]:
        if not query.strip():
            return []

        start = time.perf_counter()
        cfg = self.config
        db = cfg.snowflake.database
        table = f"{db}.AI.{cfg.embedding.embeddings_table}"

        effective_filters = filters or (infer_filters_from_query(query) if auto_filter else RetrievalFilters())
        where_sql, where_params = build_where_clause(effective_filters)

        conn = get_connection(cfg.snowflake, schema="AI")
        cursor = conn.cursor()
        try:
            cursor.execute(f"USE DATABASE {db}")
            cursor.execute("USE SCHEMA AI")

            provider = build_provider(cfg.embedding, cursor)
            query_vector = provider.embed([query])[0]
            vector_sql = format_vector_sql(query_vector, cfg.embedding.dimension)

            sql = f"""
                SELECT
                    document_id,
                    product_id,
                    warehouse,
                    risk_level,
                    document_text,
                    document_hash,
                    embedding_model,
                    VECTOR_COSINE_SIMILARITY(
                        embedding,
                        {vector_sql}
                    ) AS similarity_score
                FROM {table}
                {where_sql}
                ORDER BY similarity_score DESC
                LIMIT %s
            """
            params: list[Any] = [*where_params, top_k]
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            results = [
                RetrievedDocument(
                    document_id=row[0],
                    product_id=row[1],
                    warehouse=row[2],
                    risk_level=row[3],
                    document_text=row[4],
                    document_hash=row[5],
                    embedding_model=row[6],
                    similarity_score=float(row[7]),
                    metadata={
                        "product_id": row[1],
                        "warehouse": row[2] or "",
                        "risk_level": row[3] or "",
                    },
                )
                for row in rows
                if float(row[7]) >= min_similarity
            ]

            elapsed = time.perf_counter() - start
            logger.info(
                "retrieval_complete query_len=%s top_k=%s returned=%s latency=%.2fs filters=%s",
                len(query),
                top_k,
                len(results),
                elapsed,
                effective_filters,
            )
            return results
        finally:
            cursor.close()
            conn.close()

    def retrieve_hybrid(
        self,
        query: str,
        top_k: int = 5,
        filters: RetrievalFilters | None = None,
        keyword_weight: float = 0.15,
    ) -> list[RetrievedDocument]:
        """Semantic search with optional keyword boost on document_text."""
        semantic = self.retrieve(query, top_k=top_k * 2, filters=filters, auto_filter=False)
        if not semantic:
            return []

        q_lower = query.lower()
        tokens = [t for t in q_lower.split() if len(t) > 3]

        def hybrid_score(doc: RetrievedDocument) -> float:
            text_lower = doc.document_text.lower()
            keyword_hits = sum(1 for t in tokens if t in text_lower)
            boost = keyword_weight * keyword_hits
            return doc.similarity_score + boost

        ranked = sorted(semantic, key=hybrid_score, reverse=True)
        return ranked[:top_k]


def retrieve(
    query: str,
    top_k: int = 5,
    filters: RetrievalFilters | None = None,
    hybrid: bool = False,
) -> list[RetrievedDocument]:
    retriever = SupplyChainRetriever()
    if hybrid:
        return retriever.retrieve_hybrid(query, top_k=top_k, filters=filters)
    return retriever.retrieve(query, top_k=top_k, filters=filters)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    new_request_id()

    parser = argparse.ArgumentParser(description="Test supply chain vector retrieval")
    parser.add_argument("query", help="Natural language question")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--risk-level", default=None)
    parser.add_argument("--product-id", default=None)
    parser.add_argument("--warehouse", default=None)
    parser.add_argument("--hybrid", action="store_true")
    args = parser.parse_args(argv)

    filters = RetrievalFilters(
        risk_level=args.risk_level,
        product_id=args.product_id,
        warehouse=args.warehouse,
    )

    try:
        docs = retrieve(args.query, top_k=args.top_k, filters=filters, hybrid=args.hybrid)
        if not docs:
            print("No documents retrieved.")
            return 0

        for i, doc in enumerate(docs, start=1):
            print(f"\n--- Result {i} | score={doc.similarity_score:.4f} | {doc.document_id} ---")
            print(doc.document_text[:500])
        return 0
    except Exception:
        logger.exception("retrieval_failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
