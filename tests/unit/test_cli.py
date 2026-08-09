"""Unit tests for CLI argument parsing."""

from src.application.cli import build_parser


def test_parser_single_question():
    args = build_parser().parse_args(["-q", "Which products are at critical risk?"])
    assert args.question == "Which products are at critical risk?"
    assert args.top_k == 5
    assert args.no_hybrid is False


def test_parser_filters():
    args = build_parser().parse_args(
        ["-q", "test", "--risk-level", "CRITICAL", "--product-id", "P001", "--warehouse", "LON"]
    )
    assert args.risk_level == "CRITICAL"
    assert args.product_id == "P001"
    assert args.warehouse == "LON"
