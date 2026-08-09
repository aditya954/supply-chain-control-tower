# AI Supply Chain — Snowflake + dbt + RAG

**Interview demo:** ask supply-chain risk questions in natural language, with KPIs computed in Snowflake/dbt and answers grounded in retrieved enterprise context.

---

## Inventory Risk Assistant (recommended demo path)

Simple end-to-end track — 15 products, 5 CSVs, full AI pipeline.

```text
CSV → Snowflake RAW → dbt → AI context → Embeddings → RAG → CLI
```

### Quick start

```bash
pip install -r requirements.txt
cp .env.example .env                    # Snowflake key-pair + LLM_API_KEY

export DBT_PROFILES_DIR=$(pwd)

# Data + dbt
python3 scripts/generate_inventory_risk_data.py
python3 scripts/load_inventory_risk_to_snowflake.py
dbt build --select inventory_risk

# AI layer
python -m src.ai.embeddings
python -m src.application.cli -q "Which products are at critical risk?"
```

### Docker

```bash
docker build -t inventory-risk-assistant .
docker run -it --rm --env-file .env \
  -v $HOME/.dbt/snowflake_keys/rsa_key.p8:/secrets/key.p8:ro \
  -e SNOWFLAKE_PRIVATE_KEY_PATH=/secrets/key.p8 \
  inventory-risk-assistant -q "Why is Coconut Body Wash at risk?"
```

### Documentation

| Doc | Contents |
|-----|----------|
| [docs/project_context.md](docs/project_context.md) | Repo inspection + phase status |
| [docs/architecture.md](docs/architecture.md) | System design + Mermaid diagram |
| [docs/kpi_definitions.md](docs/kpi_definitions.md) | Deterministic KPI rules |
| [docs/deployment.md](docs/deployment.md) | Docker + GitHub Actions secrets |
| [docs/testing.md](docs/testing.md) | Test commands |
| [models/inventory_risk/README.md](models/inventory_risk/README.md) | dbt model map |

### Example question

> "Why is Coconut Body Wash at risk?"

> CRITICAL — 50 units vs 100 daily demand (0.5 days of supply), supplier OTD 72%, delayed PO/shipment → **EXPEDITE_REPLENISHMENT**

---

## Other tracks in this repo

| Track | Folder | When to use |
|-------|--------|-------------|
| **Control Tower (complex)** | `models/control_tower/` | 30-product demo with `CT_*` tables |
| **Legacy automotive** | `models/raw`, `marts/` | Enterprise dbt reference |

See original Control Tower quick start below.

---

## Control Tower (complex track)

**Interview demo project** — consumer-products pipeline with 30 products, 8 warehouses, embedded risk scenarios.

> A legacy automotive/manufacturing dbt track also lives in this repo as optional reference.

### Two-track diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CONTROL TOWER (complex demo)                                           │
│  data/*.csv → Snowflake RAW.CT_* → models/control_tower/ → MART marts   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  INVENTORY RISK ASSISTANT (simple E2E — recommended)                   │
│  data/inventory_risk/ → IR_* → models/inventory_risk/ → RAG → CLI        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Control Tower quick start

```bash
pip install -r requirements.txt
cp .env.example .env
export DBT_PROFILES_DIR=$(pwd)

python3 scripts/load_control_tower_to_snowflake.py
dbt build --select control_tower
```

---

## GitHub Actions CI/CD

Pipeline: `lint` → `unit_test` → `dbt_compile` → `dbt_test` → `ai_test` → `docker_build`

See [docs/deployment.md](docs/deployment.md) for required GitHub secrets.

Remote: `https://github.com/aditya954/supply-chain-control-tower`
