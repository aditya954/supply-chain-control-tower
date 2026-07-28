select
    s.supplier_name,
    s.supplier_tier,
    f.on_time_delivery_pct,
    f.avg_delivery_delay_days,
    f.total_deliveries
from {{ ref('dim_supplier') }} as s
inner join {{ ref('fact_supplier_performance') }} as f
    on s.supplier_id = f.supplier_id
where f.on_time_delivery_pct < 85
order by f.on_time_delivery_pct asc
limit 50
