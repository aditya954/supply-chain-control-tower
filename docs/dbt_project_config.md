# dbt_project.yml — configuration notes

The root `dbt_project.yml` configures **both** the Control Tower demo and the legacy automotive track. YAML comments are minimal; this file explains the layout.

---

## Project identity

```yaml
name: supply_chain_control_tower
profile: supply_chain_control_tower
```

Single dbt project, single Snowflake profile. Both tracks write to the same database schemas (`RAW`, `STAGING`, `INTERMEDIATE`, `MART`).

---

## Model path mapping

```
models/
├── raw/              → +schema: RAW,      +tags: ['raw']
├── staging/          → +schema: STAGING,  +tags: ['staging']
├── intermediate/     → +schema: INTERMEDIATE
├── marts/            → +schema: MART
│   ├── dimensions/   → table
│   ├── facts/        → incremental
│   └── kpis/         → table
└── control_tower/    → +tags: ['control_tower']   ← demo path
    ├── raw/          → +schema: RAW, view
    ├── staging/      → +schema: STAGING, view
    ├── intermediate/ → +schema: INTERMEDIATE, view
    └── marts/        → +schema: MART, table
```

**Why nested `control_tower/`?** Keeps demo models isolated from legacy `models/staging/stg_supplier.sql` etc., while reusing the same Snowflake schemas. Model names (`stg_ct_products` vs `stg_supplier`) prevent collisions.

---

## Selecting models

| Command | Builds |
|---------|--------|
| `dbt build --select control_tower` | Demo path only (~29 models + tests) |
| `dbt build --exclude control_tower` | Legacy automotive only |
| `dbt build` | Full project |

Tag-based alternative: `dbt build --select tag:control_tower`

---

## Vars (shared)

```yaml
vars:
  company_name: 'Enterprise Supply Chain Control Tower'
  fiscal_year_start_month: 4
  inventory_aging_buckets: [30, 60, 90, 180, 365]
  ...
```

Legacy marts use these vars. Control Tower models are mostly self-contained but inherit project-level settings.

---

## Snapshots & seeds

- **Snapshots** → `MART` schema (legacy SCD2 on `dim_*`)
- **Seeds** → `RAW` schema (`seed_region_reference.csv`)

Neither is used by the Control Tower path today.

---

## Do not change without care

- `profile:` name must match `profiles.yml`
- `+schema:` overrides — removing them would break schema separation
- `control_tower:` block — required for Phase 2 model routing

For connection settings, see `.env.example` (credentials stay in `.env`, not in this repo's tracked config).
