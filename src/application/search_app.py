"""Streamlit UI for semantic search and RAG demo."""

from __future__ import annotations

import streamlit as st

from src.ai.rag import INSUFFICIENT_DATA, SupplyChainRAG
from src.ai.retriever import RetrievalFilters, retrieve

st.set_page_config(
    page_title="Inventory Risk Search",
    page_icon="📦",
    layout="wide",
)

st.title("Supply Chain Inventory Risk Assistant")
st.caption("Semantic search over Snowflake embeddings + optional AI answer")

with st.sidebar:
    st.header("Filters")
    top_k = st.slider("Results", min_value=1, max_value=10, value=5)
    hybrid = st.checkbox("Hybrid search (semantic + keyword)", value=True)
    risk_level = st.selectbox("Risk level", ["", "CRITICAL", "HIGH", "LOW"])
    product_id = st.text_input("Product ID", placeholder="P001")
    warehouse = st.text_input("Warehouse", placeholder="LON")
    mode = st.radio("Mode", ["Semantic search", "AI answer (RAG)"])

query = st.text_input(
    "Search question",
    placeholder="e.g. Which products are at critical risk in London?",
)

if st.button("Search", type="primary") and query.strip():
    filters = RetrievalFilters(
        risk_level=risk_level or None,
        product_id=product_id or None,
        warehouse=warehouse or None,
    )

    if mode == "Semantic search":
        with st.spinner("Running vector search..."):
            docs = retrieve(query, top_k=top_k, filters=filters, hybrid=hybrid)

        if not docs:
            st.warning("No documents found. Run: python -m src.ai.embeddings")
        else:
            st.success(f"Found {len(docs)} document(s)")
            for i, doc in enumerate(docs, start=1):
                with st.expander(
                    f"#{i} {doc.document_id} | score={doc.similarity_score:.4f} | "
                    f"{doc.risk_level or 'N/A'}",
                    expanded=i == 1,
                ):
                    st.markdown(f"**Product:** {doc.product_id}  **Warehouse:** {doc.warehouse}")
                    st.text(doc.document_text)
    else:
        with st.spinner("Retrieving context and generating answer..."):
            rag = SupplyChainRAG()
            answer = rag.answer_question(
                query,
                top_k=top_k,
                filters=filters,
                hybrid=hybrid,
            )

        if answer.status == "insufficient_data":
            st.warning(INSUFFICIENT_DATA)
        else:
            st.markdown(answer.format())
            st.caption(
                f"Retrieved {answer.retrieval_count} docs | "
                f"Retrieval {answer.retrieval_latency_ms:.0f}ms | "
                f"LLM {answer.llm_latency_ms:.0f}ms"
            )

st.divider()
st.markdown(
    "**Demo tips:** try `coconut body wash`, `critical risk`, or `London warehouse`. "
    "Requires embeddings sync: `python -m src.ai.embeddings`"
)
