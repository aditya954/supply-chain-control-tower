# Testing Guide

## Test layers

| Layer | Command | Requires Snowflake |
|-------|---------|-------------------|
| Unit | `pytest tests/unit/ -v` | No |
| AI (mocked) | `pytest tests/ai/test_rag.py -v` | No |
| AI (integration) | `pytest tests/ai/test_retriever.py -v` | Yes |
| dbt | `dbt build --select inventory_risk` | Yes |

## Run all local tests (no Snowflake)

```bash
python -m pytest tests/unit/ tests/ai/test_rag.py -v
```

## dbt tests

Schema tests in `models/inventory_risk/staging/schema.yml` and `marts/schema.yml`.

Singular scenario tests:

- `tests/assert_ir_coconut_critical_risk.sql`
- `tests/assert_ir_ai_context_coconut.sql`

## RAG evaluation questions

See `tests/ai/evaluation_questions.csv` for expected entities and risk levels.

## GitHub Actions

Mirrors local test commands — see `.github/workflows/ci.yml` and [deployment.md](deployment.md).
