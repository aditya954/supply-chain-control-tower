# Enterprise Supply Chain Control Tower

## Overview

| Attribute | Value |
|-----------|-------|
| **Domain** | Manufacturing / Automotive Supply Chain |
| **Platform** | Snowflake + dbt Core + Python |
| **Database** | `ANALYTICS` (schemas: `RAW`, `STAGING`, `INTERMEDIATE`, `MART`) |

## Architecture

```
ERP/MES/TMS/QMS (simulated CSV)
        │
        ▼
   RAW schema          ← Python load script
        │
        ▼
   raw_* views         ← dbt sources
        │
        ▼
   stg_* views         ← STAGING schema
        │
        ▼
   int_* views         ← INTERMEDIATE schema
        │
        ├─► dim_* tables
        ├─► fact_* tables (incremental)
        ├─► kpi_* tables
        └─► snap_* snapshots (SCD2)
```

## Folder Structure

```
├── analyses/           # Ad-hoc analytical SQL
├── docs/               # Additional documentation
├── macros/             # Reusable SQL macros + generic tests
├── models/
│   ├── raw/            # Source-aligned views (raw_*)
│   ├── staging/        # Cleaned data (stg_*)
│   ├── intermediate/   # Business logic (int_*)
│   └── marts/
│       ├── dimensions/ # dim_*
│       ├── facts/      # fact_* (incremental)
│       └── kpis/       # kpi_*
├── sample_data/        # Generated CSV files
├── scripts/            # Python data gen + Snowflake load
├── seeds/              # Optional dbt seeds
├── snapshots/          # SCD Type 2 history
└── tests/              # Singular data tests
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate sample data

```bash
python3 scripts/generate_all_data.py
```

### 3. Configure Snowflake

Copy `.env.example` to `.env` and set credentials. The project `profiles.yml` uses:

- Database: `SUPPLY_CHAIN_DB`
- Warehouse: `DBT_WH`
- Auth: Snowflake key-pair

### 4. Load RAW tables into Snowflake

```bash
python3 scripts/load_to_snowflake.py
```

### 5. Run dbt

```bash
export DBT_PROFILES_DIR=/Users/aditya954/dbt_project
dbt deps
dbt build
dbt docs generate && dbt docs serve
```

## dbt Commands

```bash
# Full pipeline
dbt build

# Layer by layer
dbt build --select staging.*
dbt build --select intermediate.*
dbt build --select marts.dimensions.*
dbt build --select marts.facts.*
dbt build --select marts.kpis.*

# Snapshots only
dbt snapshot

# Tests only
dbt test

# Source freshness
dbt source freshness

# Incremental full refresh
dbt build --select fact_inventory --full-refresh
```

## Business KPIs

| KPI | Model |
|-----|-------|
| Inventory Turnover | `kpi_supply_chain_control_tower` |
| Days of Inventory | `kpi_supply_chain_control_tower` |
| Inventory Age | `kpi_supply_chain_control_tower` |
| Stockout Rate | `kpi_supply_chain_control_tower` |
| Supplier On-Time Delivery | `kpi_supply_chain_control_tower` |
| Supplier Lead Time | `kpi_supply_chain_control_tower` |
| Production Efficiency | `kpi_supply_chain_control_tower` |
| Machine Utilisation | `kpi_supply_chain_control_tower` |
| Scrap Rate | `kpi_supply_chain_control_tower` |
| First Pass Yield | `kpi_supply_chain_control_tower` |
| Shipment Delay Rate | `kpi_supply_chain_control_tower` |
| Average Transit Time | `kpi_supply_chain_control_tower` |
| Quality Defect Rate | `kpi_supply_chain_control_tower` |
| Warranty Claim Rate | `kpi_supply_chain_control_tower` |

## Data Volume

| Type | Tables | Rows |
|------|--------|------|
| Master | 9 | ~1,000 each (calendar: 4,018) |
| Transactional | 16 | 100,000+ each |

## Testing

- **Generic tests**: unique, not_null, relationships, accepted_values
- **Custom tests**: `positive_value`, `valid_percentage`
- **Singular tests**: `tests/assert_*.sql`
- **Unit tests**: defined in `models/staging/schema.yml`
- **Source freshness**: configured in `models/raw/sources.yml`

## Deployment

1. Create `SUPPLY_CHAIN_DB` and schemas via load script
2. Schedule `scripts/load_to_snowflake.py` for RAW ingestion
3. Run `dbt build` in CI/CD on merge to main
4. Run snapshots daily for SCD2 history
5. Exclude unit tests in production: `dbt build --exclude-resource-type unit_test`
