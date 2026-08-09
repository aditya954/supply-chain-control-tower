"""AI RAG tests with mocked retrieval and LLM."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.ai.rag import (
    INSUFFICIENT_DATA,
    SupplyChainRAG,
    parse_llm_response,
)
from src.ai.retriever import RetrievedDocument


def _doc(doc_id: str, product_id: str, text: str, risk: str = "CRITICAL") -> RetrievedDocument:
    return RetrievedDocument(
        document_id=doc_id,
        product_id=product_id,
        warehouse="LON",
        risk_level=risk,
        document_text=text,
        document_hash="hash",
        similarity_score=0.91,
        embedding_model="test-model",
    )


class TestParseResponse:
    def test_parses_structured_sections(self):
        raw = """Risk:
CRITICAL

Key Reasons:
- Inventory covers only 0.5 days of demand.
- Supplier OTD is 72%.

Business Impact:
Potential stockout.

Recommended Action:
Expedite replenishment.

Supporting Sources:
DOC_P001, PO001

Confidence:
High"""
        parsed = parse_llm_response(raw, fallback_sources=["DOC_P001"])
        assert parsed["risk"] == "CRITICAL"
        assert len(parsed["reasons"]) == 2
        assert "PO001" in parsed["sources"]


class TestRAGSafety:
    def test_no_retrieval_returns_insufficient_data_without_llm(self):
        retriever = MagicMock()
        retriever.retrieve_hybrid.return_value = []
        llm = MagicMock()

        rag = SupplyChainRAG(retriever=retriever, llm_provider=llm)
        answer = rag.answer_question("Why is P999 critical?")

        assert answer.status == "insufficient_data"
        assert answer.raw_response == INSUFFICIENT_DATA
        llm.complete.assert_not_called()

    def test_unknown_product_filter_empty_results(self):
        retriever = MagicMock()
        retriever.retrieve_hybrid.return_value = []
        llm = MagicMock()

        rag = SupplyChainRAG(retriever=retriever, llm_provider=llm)
        answer = rag.answer_question("Why is product P999 critical?")

        assert answer.status == "insufficient_data"
        assert answer.sources == []

    def test_critical_product_includes_sources(self):
        coconut_doc = _doc(
            "DOC_P001",
            "P001",
            "Product: Coconut Body Wash\nPurchase Order: PO001\nSupplier: S001\nOverall Risk: CRITICAL",
        )
        retriever = MagicMock()
        retriever.retrieve_hybrid.return_value = [coconut_doc]

        llm = MagicMock()
        llm.complete.return_value = """Risk:
CRITICAL

Key Reasons:
- Low days of supply.

Business Impact:
Stockout risk.

Recommended Action:
EXPEDITE_REPLENISHMENT

Supporting Sources:
DOC_P001, PO001

Confidence:
High"""

        rag = SupplyChainRAG(retriever=retriever, llm_provider=llm)
        answer = rag.answer_question("Why is Coconut Body Wash at risk?")

        assert answer.status == "success"
        assert "DOC_P001" in answer.sources
        assert answer.risk == "CRITICAL"
        llm.complete.assert_called_once()

    def test_supplier_question_retrieves_documents(self):
        doc = _doc("DOC_P001", "P001", "Supplier OTD: 72%\nOverall Risk: CRITICAL")
        retriever = MagicMock()
        retriever.retrieve_hybrid.return_value = [doc]
        llm = MagicMock()
        llm.complete.return_value = "Risk:\nHIGH\nKey Reasons:\n- Poor OTD\nBusiness Impact:\nDelays\nRecommended Action:\nReview supplier\nSupporting Sources:\nDOC_P001\nConfidence:\nMedium"

        answer = SupplyChainRAG(retriever=retriever, llm_provider=llm).answer_question(
            "Which suppliers are causing the biggest problems?"
        )
        assert answer.retrieval_count == 1
        assert "DOC_P001" in answer.sources
