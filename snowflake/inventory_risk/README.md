# Snowflake DDL — Inventory Risk Assistant

SQL setup for the **simple AI inventory-risk demo**. Executed by `scripts/load_inventory_risk_to_snowflake.py`.

## Run order

| Script | Purpose |
|--------|---------|
| `01_schemas.sql` | Ensure `RAW`, `STAGING`, `MART`, `AI` exist |
| `02_raw_tables.sql` | `IR_*` table DDL |
| `03_validate.sql` | Post-load checks (manual or after load) |
| `04_ai_vector_table.sql` | `IR_DOCUMENT_EMBEDDINGS` vector storage |

## Load data

```bash
python3 scripts/generate_inventory_risk_data.py   # if CSVs missing
python3 scripts/load_inventory_risk_to_snowflake.py
```

## Table prefix

`IR_*` avoids collision with legacy `INVENTORY` / `supplier` and Control Tower `CT_*` tables in the same `RAW` schema.

| CSV | Snowflake table |
|-----|-----------------|
| `inventory.csv` | `IR_INVENTORY` |
| `suppliers.csv` | `IR_SUPPLIERS` |
| `purchase_orders.csv` | `IR_PURCHASE_ORDERS` |
| `shipments.csv` | `IR_SHIPMENTS` |
| `forecast.csv` | `IR_FORECAST` |
