"""Unit tests for embedding hash-based incremental logic."""

from src.ai.embeddings import ContextDocument, documents_needing_embedding


def _doc(doc_id: str, doc_hash: str) -> ContextDocument:
    return ContextDocument(
        document_id=doc_id,
        product_id=doc_id.replace("DOC_", ""),
        warehouse="LON",
        risk_level="LOW",
        document_text="sample",
        document_hash=doc_hash,
    )


def test_documents_needing_embedding_new_document():
    docs = [_doc("DOC_P001", "hash_a")]
    existing: dict[str, str] = {}
    result = documents_needing_embedding(docs, existing)
    assert len(result) == 1
    assert result[0].document_id == "DOC_P001"


def test_documents_needing_embedding_unchanged_hash_skipped():
    docs = [_doc("DOC_P001", "hash_a")]
    existing = {"DOC_P001": "hash_a"}
    result = documents_needing_embedding(docs, existing)
    assert result == []


def test_documents_needing_embedding_changed_hash_reembedded():
    docs = [_doc("DOC_P001", "hash_b")]
    existing = {"DOC_P001": "hash_a"}
    result = documents_needing_embedding(docs, existing)
    assert len(result) == 1
    assert result[0].document_hash == "hash_b"


def test_documents_needing_embedding_mixed_batch():
    docs = [
        _doc("DOC_P001", "hash_a"),
        _doc("DOC_P002", "hash_new"),
        _doc("DOC_P003", "hash_c"),
    ]
    existing = {"DOC_P001": "hash_a", "DOC_P002": "hash_old", "DOC_P003": "hash_c"}
    result = documents_needing_embedding(docs, existing)
    assert [d.document_id for d in result] == ["DOC_P002"]
