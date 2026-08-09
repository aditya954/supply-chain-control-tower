with risk as (

    select * from {{ ref('int_ct_product_risk') }}

),

products as (

    select * from {{ ref('stg_ct_products') }}

),

warehouses as (

    select * from {{ ref('stg_ct_warehouses') }}

)

select
    r.product_id,
    p.product_name,
    p.category,
    r.warehouse_id,
    w.warehouse_name,
    w.country as warehouse_country,
    r.supplier_id,
    r.supplier_name,
    r.available_qty,
    r.daily_demand,
    r.days_of_supply,
    r.is_stockout_risk,
    r.is_excess_inventory,
    r.is_slow_moving,
    r.forecast_accuracy_pct,
    r.forecast_bias_pct,
    r.forward_forecast_daily_demand,
    r.supplier_otd_pct,
    r.supplier_otif_pct,
    r.is_supplier_risk,
    r.shipment_delay_rate_pct,
    r.avg_delivery_delay_days,
    r.fill_rate_pct,
    r.backorder_rate_pct,
    r.otif_pct,
    r.customer_impact_pct,
    r.warehouse_utilization_pct,
    r.is_capacity_risk,
    r.risk_signal_count,
    current_timestamp() as last_updated_at
from risk as r
inner join products as p
    on r.product_id = p.product_id
inner join warehouses as w
    on r.warehouse_id = w.warehouse_id
