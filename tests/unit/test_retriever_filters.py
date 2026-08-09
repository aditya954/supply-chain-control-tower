"""Unit tests for retrieval filter SQL building."""

from src.ai.retriever import RetrievalFilters, build_where_clause, infer_filters_from_query


def test_build_where_clause_empty():
    sql, params = build_where_clause(None)
    assert sql == ""
    assert params == []


def test_build_where_clause_risk_level():
    sql, params = build_where_clause(RetrievalFilters(risk_level="CRITICAL"))
    assert sql == "WHERE risk_level = %s"
    assert params == ["CRITICAL"]


def test_build_where_clause_multiple_filters():
    filters = RetrievalFilters(risk_level="HIGH", product_id="P001", warehouse="LON")
    sql, params = build_where_clause(filters)
    assert "risk_level = %s" in sql
    assert "product_id = %s" in sql
    assert "warehouse = %s" in sql
    assert params == ["HIGH", "P001", "LON"]


def test_build_where_clause_keyword():
    sql, params = build_where_clause(RetrievalFilters(keyword="supplier"))
    assert "document_text ILIKE %s" in sql
    assert params == ["%supplier%"]


def test_infer_filters_critical_risk():
    filters = infer_filters_from_query("Which products are at critical risk today?")
    assert filters.risk_level == "CRITICAL"


def test_infer_filters_coconut_product():
    filters = infer_filters_from_query("Why is Coconut Body Wash at risk?")
    assert filters.product_id == "P001"


def test_infer_filters_london_warehouse():
    filters = infer_filters_from_query("What is the risk in London?")
    assert filters.warehouse == "LON"
