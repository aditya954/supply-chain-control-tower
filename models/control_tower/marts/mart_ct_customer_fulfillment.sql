with fulfillment as (

    select * from {{ ref('int_ct_order_fulfillment') }}

),

products as (

    select * from {{ ref('stg_ct_products') }}

),

warehouses as (

    select * from {{ ref('stg_ct_warehouses') }}

)

select
    f.product_id,
    p.product_name,
    f.warehouse_id,
    w.warehouse_name,
    f.total_order_count,
    f.total_order_qty,
    f.fulfilled_qty,
    f.backorder_count,
    f.fill_rate_pct,
    f.backorder_rate_pct,
    f.otif_pct,
    f.at_risk_customer_qty,
    f.customer_impact_pct,
    current_timestamp() as last_updated_at
from fulfillment as f
inner join products as p
    on f.product_id = p.product_id
inner join warehouses as w
    on f.warehouse_id = w.warehouse_id
