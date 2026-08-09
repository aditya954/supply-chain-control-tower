# Project Context — AI Supply Chain Inventory Risk Assistant

**Inspected:** 2026-08-09  
**Goal:** Extend this repo with a **simple end-to-end** inventory-risk assistant (Snowflake → dbt → AI context → RAG → CLI) without replacing existing work.

---

## What already exists

### Three tracks in one repository

| Track | Purpose | Location | Snowflake RAW |
|-------|---------|----------|---------------|
| **Legacy automotive** | Enterprise dbt reference | `models/raw`, `staging`, `marts` | `supplier`, `inventory`, `dim_*`, etc. |
| **Control Tower (complex)** | Prior interview demo (30 products, 8 warehouses) | `models/control_tower/` | `CT_*` tables |
| **Inventory Risk Assistant (NEW)** | Simple E2E AI demo (this task) | `data/inventory_risk/`, `models/inventory_risk/` (Phases 2+) | `IR_*` tables (Phase 2) |

All tracks share:

| Config | Value |
|--------|-------|
| Database | `ANALYTICS` |
| Warehouse | `DBT_WH` |
| Role | `TRANSFORMER` |
| Profile | `supply_chain_control_tower` (`profiles.yml`) |
| Auth | Key-pair (`.env`) |

Schemas in use: `RAW`, `STAGING`, `INTERMEDIATE`, `MART`, `SEMANTIC`, `AI` (last two exist in DDL; minimal models today).

### dbt project

- **File:** `dbt_project.yml` at repo root (not nested `dbt/`)
- **Model paths:** `models/` with layer folders
- **Existing staging names:** `stg_inventory`, `stg_suppliers`, etc. → **cannot reuse** for the new assistant
- **Convention for new work:** `models/inventory_risk/` with `ir_` / `stg_ir_*` / `mart_ir_*` prefixes and tag `inventory_risk`

### Python

| Exists | Path |
|--------|------|
| Control Tower data gen/load | `scripts/generate_control_tower_data.py`, `load_control_tower_to_snowflake.py` |
| Legacy load | `scripts/load_to_snowflake.py` |
| **Not yet** | `src/` (RAG, embeddings, CLI) — Phases 5–8 |

### Docker / CI

| Item | Status |
|------|--------|
| `Dockerfile` | Not present |
| `.github/workflows/ci.yml` | GitHub Actions pipeline |
| Git remote | GitHub (`github.com/aditya954/supply-chain-control-tower`) |

### Data on disk

| Folder | Contents |
|--------|----------|
| `data/` | Control Tower CSVs (`CT_*` loader) — **do not overwrite** |
| `data/inventory_risk/` | **NEW** — 5 simple CSVs for this assistant |
| `sample_data/` | Legacy automotive (gitignored) |

---

## Where the new project is added

```text
data/inventory_risk/          ← Phase 1 sample data (5 CSVs)
snowflake/inventory_risk/     ← Phase 2 DDL + load (planned)
models/inventory_risk/        ← Phase 3–4 dbt + AI context (planned)
  staging/
  intermediate/
  marts/
  ai/
src/                          ← Phase 5–8 Python RAG + CLI (planned)
tests/unit/, tests/ai/        ← Phase 6+ tests (planned)
docs/architecture.md          ← Phase 10 docs (planned)
Dockerfile, `.github/workflows/ci.yml`    ← Phases 9–10
```

### Naming to avoid collisions

| User spec name | Our implementation | Reason |
|----------------|------------------|--------|
| `RAW.INVENTORY` | `RAW.IR_INVENTORY` | `INVENTORY` already used by legacy track |
| `stg_inventory.sql` | `models/inventory_risk/staging/stg_ir_inventory.sql` | `stg_inventory` exists |
| `mart_supply_chain_risk` | `mart_ir_supply_chain_risk` | Distinct from `mart_ct_supply_chain_risk` |

Logic and columns follow the task spec; only names are prefixed.

---

## Phase roadmap (this task)

| Phase | Scope | Status |
|-------|-------|--------|
| **1** | Inspect + sample data | **Done** (`data/inventory_risk/`) |
| **2** | Snowflake `IR_*` RAW tables + load scripts | **Done** |
| **3** | dbt staging → intermediate → mart | **Done** |
| **4** | `ai_ir_supply_chain_context` model | **Done** |
| **5** | Embedding pipeline | **Done** |
| **6** | Vector retrieval (`src/ai/retriever.py`) | **Done** |
| **7** | RAG + prompts (`src/ai/rag.py`) | **Done** |
| **8** | CLI (`src/application/cli.py`) | **Done** |
| **9** | Docker | **Done** |
| **10** | GitHub Actions CI/CD + docs | **Done** |

---

## Demo scenarios baked into Phase 1 data

| Tier | Products | Story |
|------|----------|-------|
| **CRITICAL** | Coconut Body Wash, Baby Formula, Frozen Pizza | &lt;1 day supply, delayed PO/shipment, poor supplier OTD |
| **HIGH** | Dark Chocolate, Energy Drink, Sunscreen | &lt;2 days supply or supplier OTD &lt;80% |
| **MEDIUM** | Olive Oil, Pasta, Granola | 2–5 days supply, minor delays |
| **HEALTHY** | Sparkling Water, Green Tea, Rice, Detergent, Hand Soap, Vitamin C | Adequate stock, on-time supply |

Interview headline example: **Coconut Body Wash @ London** — 50 units vs 100 daily demand (0.5 DOS), supplier OTD 72%, PO and shipment DELAYED.

---

## Commands (Phase 1)

```bash
# Regenerate simple dataset
python3 scripts/generate_inventory_risk_data.py

# Validate row counts
wc -l data/inventory_risk/*.csv
```

Phase 2+ commands will be added as each phase completes.
