"""CLI formatting helpers."""

from __future__ import annotations

from src.ai.rag import RAGAnswer


def format_answer_for_cli(answer: RAGAnswer) -> str:
    return answer.format()
