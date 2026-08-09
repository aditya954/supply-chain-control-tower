# Control Tower source data

Synthetic CSV files for the **AI Supply Chain Control Tower** demo. Loaded into Snowflake as `ANALYTICS.RAW.CT_*` tables.

## Files

| CSV | Snowflake table | Rows | Description |
|-----|-----------------|------|-------------|
| `products.csv` | `CT_PRODUCTS` | 30 | Product master (SKU, category) |
| `warehouses.csv` | `CT_WAREHOUSES` | 8 | Global warehouses with capacity |
| `suppliers.csv` | `CT_SUPPLIERS` | 15 | Supplier master with OTD/OTIF |
| `inventory.csv` | `CT_INVENTORY` | 500 | Stock snapshots by product × warehouse |
| `demand.csv` | `CT_DEMAND` | 14,280 | 90-day history + 30-day forecast |
| `purchase_orders.csv` | `CT_PURCHASE_ORDERS` | 500 | PO lines with receipt status |
| `shipments.csv` | `CT_SHIPMENTS` | 500 | Inbound shipments linked to POs |
| `sales_orders.csv` | `CT_SALES_ORDERS` | 1,000 | Customer orders with fulfillment status |

## Regenerate

```bash
python3 scripts/generate_control_tower_data.py
```

Uses fixed seed (`20260809`) for reproducible risk scenarios (Coconut Water stockout, capacity pressure, etc.).

## Load to Snowflake

```bash
python3 scripts/load_control_tower_to_snowflake.py
```

> **Note:** `sample_data/` at repo root is the **legacy automotive** dataset — not used by Control Tower.
