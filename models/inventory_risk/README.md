# Inventory Risk Assistant — dbt models

Simple pipeline for the AI inventory-risk demo. Run with tag `inventory_risk`.

## Layers

| Layer | Models | Schema |
|-------|--------|--------|
| raw | `raw_ir_*` (5) | RAW |
| staging | `stg_ir_*` (5) | STAGING |
| intermediate | `int_ir_supply_chain_risk` | INTERMEDIATE |
| marts | `mart_ir_supply_chain_risk` | MART |
| ai | `ai_ir_supply_chain_context` | AI |

## Build

```bash
export DBT_PROFILES_DIR=$(pwd)
dbt build --select inventory_risk
```

## Embeddings (Phase 5)

```bash
# Requires .env with Snowflake key-pair credentials (see .env.example)
python -m src.ai.embeddings
```

Incremental: only documents with changed `document_hash` are re-embedded.
Results stored in `ANALYTICS.AI.IR_DOCUMENT_EMBEDDINGS`.

## Retrieval (Phase 6)

```bash
python -m src.ai.retriever "Which products are at critical risk?"
python -m src.ai.retriever "Why is Coconut Body Wash at risk?" --top-k 3
python -m src.ai.retriever "supplier problems" --risk-level CRITICAL --hybrid
```

Uses `VECTOR_COSINE_SIMILARITY` on `IR_DOCUMENT_EMBEDDINGS` with optional metadata filters.

## RAG (Phase 7)

```python
from src.ai.rag import answer_question
print(answer_question("Why is Coconut Body Wash at risk?").format())
```

Requires embeddings synced and `LLM_API_KEY` or `LLM_PROVIDER=cortex` with Snowflake Cortex access.

## CLI (Phase 8)

```bash
# Single question
python -m src.application.cli -q "Which products are at critical risk?"

# Interactive mode
python -m src.application.cli

# With filters
python -m src.application.cli -q "Why is Coconut Body Wash at risk?" --product-id P001
```

## Headline mart

`mart_ir_supply_chain_risk` — one row per product with days of supply, risk levels, and `recommended_action`.

Interview example: `product_id = 'P001'` (Coconut Body Wash) → CRITICAL, EXPEDITE_REPLENISHMENT.
