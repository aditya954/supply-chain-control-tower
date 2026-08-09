# KPI Definitions — Inventory Risk Assistant

All KPIs are calculated **deterministically in dbt** (`mart_ir_supply_chain_risk`). The LLM explains them but never computes them.

---

## Days of Supply (DOS)

```
days_of_supply = stock_qty / daily_demand
```

| Example | Calculation | Result |
|---------|-------------|--------|
| Coconut Body Wash | 50 / 100 | **0.5 days** |

Interpretation: How many days current stock will last at current demand rate.

---

## Reorder Point

```
reorder_point = daily_demand × lead_time_days
```

| Example | Calculation | Result |
|---------|-------------|--------|
| Coconut Body Wash | 100 × 7 | **700 units** |

Interpretation: Inventory level that should trigger replenishment given lead time.

---

## Supplier OTD %

Source: `supplier_otd_pct` from `IR_SUPPLIERS` (master data).

Interpretation: Historical on-time delivery performance for the supplier.

---

## Supplier Risk

| Rule | Level |
|------|-------|
| `supplier_otd_pct < 80` | **HIGH** |
| Otherwise | **LOW** |

---

## Shipment Risk

| Rule | Level |
|------|-------|
| `shipment_status = 'DELAYED'` | **HIGH** |
| Otherwise | **LOW** |

---

## Inventory Risk

| Rule | Level |
|------|-------|
| `days_of_supply < 1` | **CRITICAL** |
| `days_of_supply < 2` | **HIGH** |
| Otherwise | **LOW** |

---

## Overall Risk

Deterministic rules in `mart_ir_supply_chain_risk`:

| Condition | Overall Risk |
|-----------|--------------|
| `days_of_supply < 1` AND `shipment_status = 'DELAYED'` | **CRITICAL** |
| `days_of_supply < 2` OR `supplier_otd_pct < 80` | **HIGH** |
| Otherwise | **LOW** |

---

## Recommended Action

| Condition | Action |
|-----------|--------|
| CRITICAL + DELAYED shipment | `EXPEDITE_REPLENISHMENT` |
| HIGH + supplier OTD < 80% | `REVIEW_SUPPLIER` |
| HIGH + excess inventory elsewhere | `CONSIDER_REALLOCATION` |
| Otherwise | `MONITOR` |

---

## Model lineage

```
stg_ir_inventory ──┐
stg_ir_suppliers ──┤
stg_ir_purchase_orders ──┼──► int_ir_supply_chain_risk ──► mart_ir_supply_chain_risk ──► ai_ir_supply_chain_context
stg_ir_shipments ──┤
stg_ir_forecast ───┘
```

---

## Interview talking points

1. **Why separate KPI layer?** — Prevents LLM hallucination of inventory numbers.
2. **Why document_hash?** — Cost-efficient incremental embeddings.
3. **Why IR_ prefix?** — Coexists with legacy `INVENTORY` and `CT_*` tables.
4. **Headline demo** — Coconut Body Wash: 0.5 DOS, 72% OTD, DELAYED PO → CRITICAL → EXPEDITE_REPLENISHMENT.
