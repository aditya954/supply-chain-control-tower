with shipments as (

    select * from {{ ref('int_ct_shipment_performance') }}

),

products as (

    select * from {{ ref('stg_ct_products') }}

),

suppliers as (

    select * from {{ ref('stg_ct_suppliers') }}

)

select
    s.product_id,
    p.product_name,
    s.supplier_id,
    sup.supplier_name,
    s.shipment_count,
    s.delayed_shipment_count,
    s.shipment_delay_rate_pct,
    s.on_time_shipment_rate_pct,
    s.avg_delivery_delay_days,
    s.supplier_shipment_delay_rate_pct,
    s.supplier_on_time_shipment_rate_pct,
    current_timestamp() as last_updated_at
from shipments as s
inner join products as p
    on s.product_id = p.product_id
inner join suppliers as sup
    on s.supplier_id = sup.supplier_id
