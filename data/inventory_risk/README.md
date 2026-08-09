# Inventory Risk Assistant — source data

Five intentional CSV files for the **simple end-to-end AI demo**.  
Separate from `data/` Control Tower files (`CT_*` loader) — do not mix loaders.

## Files

| CSV | Rows | Description |
|-----|------|-------------|
| `inventory.csv` | 15 | Product stock and daily demand by warehouse |
| `suppliers.csv` | 15 | Supplier lead time and OTD % per product |
| `purchase_orders.csv` | 15 | Open / delayed / received POs |
| `shipments.csv` | 15 | Linked inbound shipments |
| `forecast.csv` | 18 | Near-term demand forecast |

## Risk scenarios

| Tier | Count | Example |
|------|-------|---------|
| CRITICAL | 3 | Coconut Body Wash — 50 stock, 100 demand, delayed PO |
| HIGH | 4 | Dark Chocolate — low buffer + supplier OTD 78% |
| MEDIUM | 4 | Olive Oil — moderate days of supply |
| HEALTHY | 4 | Sparkling Water — 20 days of supply |

## Regenerate

```bash
python3 scripts/generate_inventory_risk_data.py
```

Loaded to Snowflake as `IR_*` tables in Phase 2 (`scripts/load_inventory_risk_to_snowflake.py`).
