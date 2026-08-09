# Control Tower dbt models

**Interview demo path.** Transforms `RAW.CT_*` tables into risk and health marts.

## Layer structure

```
raw/           raw_ct_*        → views over sources (sources.yml)
staging/       stg_ct_*        → cleaned, typed columns
intermediate/  int_ct_*        → business logic & joins
marts/         mart_ct_*       → analytics tables (materialized)
```

## Start here

| File | Why |
|------|-----|
| `marts/mart_ct_supply_chain_risk.sql` | Unified risk scorecard — best demo entry point |
| `intermediate/int_ct_product_risk.sql` | Core risk logic |
| `raw/sources.yml` | Source definitions + freshness |
| `staging/schema.yml` | Column tests on staging |
| `marts/schema.yml` | Mart documentation & tests |

## Build

```bash
dbt build --select control_tower
```

## Naming

All models use the `*_ct_*` prefix to distinguish from legacy automotive models in `models/staging/`, `models/marts/`, etc.
