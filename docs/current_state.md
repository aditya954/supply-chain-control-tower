# Current State

**Updated:** 2026-08-09 (close-out)  
**Demo path:** AI Supply Chain Control Tower (`models/control_tower/`)

---

## Status at a glance

| Phase | Scope | Status |
|-------|-------|--------|
| **1** | CSV dataset, Snowflake DDL, `CT_*` RAW load | **Done** |
| **2** | dbt `models/control_tower/` (raw → marts) + tests | **Done** |
| **3** | Semantic layer (`SEMANTIC`, MetricFlow metrics) | Pending |
| **4** | AI-ready views / features (`AI` schema) | Pending |
| **5** | Python `src/` RAG / agent package | Pending |
| **6** | API or chat UI over marts | Pending |
| **7** | Observability, alerting on risk marts | Pending |
| **8** | CI/CD (GitHub Actions), scheduled runs | Pending |

| Area | Status | Notes |
|------|--------|-------|
| Legacy automotive dbt | **Done** (reference) | Unchanged; run with `--exclude control_tower` |
| Documentation | **Done** | README, `project_guide.md`, folder READMEs |

**Blockers:** None for Phases 1–2.

---

## Phase 2 validation (2026-08-09)

```bash
export DBT_PROFILES_DIR=$(pwd)
dbt build --select control_tower
```

| Result | Count |
|--------|-------|
| Models built | 29 |
| Tests passed | 62 (60 schema + 2 singular) |
| Total nodes | 91 (incl. 2 on-run hooks) |
| Failures | 0 |

Singular scenario tests: `assert_ct_coconut_london_stockout_risk`, `assert_ct_high_risk_suppliers_flagged` — both **pass**.

Headline mart `mart_ct_supply_chain_risk`: 240 product–warehouse rows.

---

## Snowflake

| Setting | Value |
|---------|-------|
| Database | `ANALYTICS` |
| Warehouse | `DBT_WH` |
| Role | `TRANSFORMER` |
| Auth | Key-pair via `.env` |
| Profile | `supply_chain_control_tower` (`profiles.yml` in repo root) |

### Control Tower RAW tables

| Table | Rows |
|-------|------|
| `CT_PRODUCTS` | 30 |
| `CT_WAREHOUSES` | 8 |
| `CT_SUPPLIERS` | 15 |
| `CT_INVENTORY` | 500 |
| `CT_DEMAND` | 14,280 |
| `CT_PURCHASE_ORDERS` | 500 |
| `CT_SHIPMENTS` | 500 |
| `CT_SALES_ORDERS` | 1,000 |

Legacy automotive tables (no `CT_` prefix) also exist in `RAW` from the original project.

---

## dbt layers (Control Tower)

| Layer | Schema | Models | Materialization |
|-------|--------|--------|-----------------|
| raw | `RAW` | `raw_ct_*` (8) | view |
| staging | `STAGING` | `stg_ct_*` (8) | view |
| intermediate | `INTERMEDIATE` | `int_ct_*` (7) | view |
| marts | `MART` | `mart_ct_*` (6) | table |

---

## Key files

| Path | Role |
|------|------|
| `data/*.csv` | Source files |
| `snowflake/01`–`05_*.sql` | DDL + validation |
| `scripts/load_control_tower_to_snowflake.py` | Phase 1 loader |
| `models/control_tower/` | Phase 2 dbt project |
| `tests/assert_ct_*.sql` | Scenario validation tests |
| `docs/project_guide.md` | Architecture and phase roadmap |

---

## Git

| Item | Value |
|------|-------|
| Remote | `github.com/aditya954/supply-chain-control-tower` |
| Branches | `dev`, `main`, `supply_chain` |
| Uncommitted | Phase 1–2 Control Tower work (not yet committed) |

---

## Recommended next step (Phase 3)

Define semantic models and MetricFlow metrics on `mart_ct_*` tables, starting with `mart_ct_supply_chain_risk` KPIs (stockout rate, supplier risk count, capacity utilization).
