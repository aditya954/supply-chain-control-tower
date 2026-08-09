# Snowflake DDL scripts

SQL setup for the **Control Tower** RAW layer. Executed in order by `scripts/load_control_tower_to_snowflake.py`.

## Run order

| Script | Purpose |
|--------|---------|
| `01_database.sql` | `USE DATABASE ANALYTICS` |
| `02_schemas.sql` | Create `RAW`, `STAGING`, `INTERMEDIATE`, `MART`, `SEMANTIC`, `AI` |
| `03_raw_tables.sql` | `CT_*` table DDL |
| `04_stages.sql` | `CT_CSV_STAGE` file format + stage (for bulk COPY if needed) |
| `05_load_data.sql` | Post-load validation queries (run manually or after load) |

## Manual execution

```bash
# From Snowflake worksheet, run 01 → 04 in order, then load via Python script
python3 scripts/load_control_tower_to_snowflake.py
```

The Python loader handles DDL (01–04) and pandas-based inserts. `05_load_data.sql` is for row-count / FK sanity checks.

## Table prefix

All Control Tower tables use `CT_*` to avoid colliding with legacy automotive RAW tables (`supplier`, `inventory`, etc.) in the same `RAW` schema.
