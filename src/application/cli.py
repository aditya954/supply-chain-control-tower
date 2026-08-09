#!/usr/bin/env python3
"""Supply Chain Inventory Risk Assistant — interactive CLI."""

from __future__ import annotations

import argparse
import sys

from src.ai.rag import INSUFFICIENT_DATA, SupplyChainRAG
from src.ai.retriever import RetrievalFilters
from src.logging_config import configure_logging, new_request_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI Supply Chain Inventory Risk Assistant",
        epilog="Example: python -m src.application.cli -q \"Which products are at critical risk?\"",
    )
    parser.add_argument(
        "-q",
        "--question",
        help="Single question to answer (omit for interactive mode)",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Number of documents to retrieve")
    parser.add_argument("--risk-level", help="Filter by risk level (LOW, HIGH, CRITICAL)")
    parser.add_argument("--product-id", help="Filter by product ID (e.g. P001)")
    parser.add_argument("--warehouse", help="Filter by warehouse code (e.g. LON)")
    parser.add_argument(
        "--no-hybrid",
        action="store_true",
        help="Disable hybrid (semantic + keyword) retrieval",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def print_banner() -> None:
    print("=" * 60)
    print("  Supply Chain Inventory Risk Assistant")
    print("  Powered by Snowflake + dbt + RAG")
    print("=" * 60)
    print("Type a question, or 'exit' / 'quit' to leave.\n")


def run_question(rag: SupplyChainRAG, question: str, args: argparse.Namespace) -> int:
    filters = RetrievalFilters(
        risk_level=args.risk_level,
        product_id=args.product_id,
        warehouse=args.warehouse,
    )

    print("Searching supply-chain data...\n")
    answer = rag.answer_question(
        question,
        top_k=args.top_k,
        filters=filters,
        hybrid=not args.no_hybrid,
    )

    if answer.status == "insufficient_data":
        print(INSUFFICIENT_DATA)
        return 0

    print(answer.format())
    print(
        f"\n---\nRetrieved {answer.retrieval_count} document(s) | "
        f"Model: {answer.model} | "
        f"Retrieval: {answer.retrieval_latency_ms:.0f}ms | "
        f"LLM: {answer.llm_latency_ms:.0f}ms"
    )
    return 0


def interactive_loop(rag: SupplyChainRAG, args: argparse.Namespace) -> int:
    print_banner()
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not question:
            continue
        if question.lower() in {"exit", "quit", "q"}:
            print("Goodbye.")
            return 0

        try:
            run_question(rag, question, args)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
        print()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    configure_logging(args.log_level)
    new_request_id()

    rag = SupplyChainRAG()

    if args.question:
        try:
            return run_question(rag, args.question, args)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    return interactive_loop(rag, args)


if __name__ == "__main__":
    sys.exit(main())
