select
    k.year_month,
    k.inventory_turnover,
    k.days_of_inventory,
    k.stockout_rate,
    k.supplier_on_time_delivery_pct,
    k.production_efficiency_pct,
    k.first_pass_yield_pct,
    k.shipment_delay_rate
from {{ ref('kpi_supply_chain_control_tower') }} as k
where k.year_month >= to_char(dateadd('month', -12, current_date()), 'YYYY-MM')
order by k.year_month desc
