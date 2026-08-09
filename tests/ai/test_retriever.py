"""Integration tests for vector retrieval (requires Snowflake + embeddings)."""

from __future__ import annotations

import os

import pytest

from src.ai.retriever import RetrievalFilters, SupplyChainRetriever
from src.config import load_config


def _snowflake_configured() -> bool:
    cfg = load_config()
    return bool(cfg.snowflake.account and cfg.snowflake.user)


pytestmark = pytest.mark.skipif(
    not _snowflake_configured(),
    reason="Snowflake credentials not configured in .env",
)


@pytest.fixture
def retriever() -> SupplyChainRetriever:
    return SupplyChainRetriever()


def test_retrieve_critical_products(retriever: SupplyChainRetriever):
    docs = retriever.retrieve(
        "Which products are at critical risk?",
        top_k=5,
        filters=RetrievalFilters(risk_level="CRITICAL"),
        auto_filter=False,
    )
    assert docs, "Expected critical-risk documents"
    assert all(d.risk_level == "CRITICAL" for d in docs)


def test_retrieve_coconut_by_product_filter(retriever: SupplyChainRetriever):
    docs = retriever.retrieve(
        "inventory risk",
        top_k=1,
        filters=RetrievalFilters(product_id="P001"),
        auto_filter=False,
    )
    assert len(docs) == 1
    assert docs[0].product_id == "P001"
    assert "Coconut Body Wash" in docs[0].document_text


def test_retrieve_unknown_product_returns_empty(retriever: SupplyChainRetriever):
    docs = retriever.retrieve(
        "Why is P999 critical?",
        top_k=5,
        filters=RetrievalFilters(product_id="P999"),
        auto_filter=False,
    )
    assert docs == []
