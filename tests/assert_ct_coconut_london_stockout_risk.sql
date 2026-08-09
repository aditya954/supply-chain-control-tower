-- Coconut Water at London should show stockout risk in Phase 2 marts
select *
from {{ ref('mart_ct_inventory_health') }}
where product_id = 'P001'
  and warehouse_id = 'W01'
  and is_stockout_risk = false
