with inventory as (

    select * from {{ ref('stg_ir_inventory') }}

),

suppliers as (

    select * from {{ ref('stg_ir_suppliers') }}

),

purchase_orders as (

    select * from {{ ref('stg_ir_purchase_orders') }}

),

shipments as (

    select * from {{ ref('stg_ir_shipments') }}

),

forecast as (

    select
        product_id,
        forecast_demand
    from {{ ref('stg_ir_forecast') }}
    qualify row_number() over (
        partition by product_id
        order by forecast_date desc
    ) = 1

),

joined as (

    select
        i.product_id,
        i.product_name,
        i.warehouse,
        i.stock_qty,
        i.daily_demand,
        i.snapshot_date,
        s.supplier_id,
        s.supplier_name,
        s.lead_time_days,
        s.supplier_otd_pct,
        po.po_id,
        po.ordered_qty,
        po.expected_date as po_expected_date,
        po.status as po_status,
        sh.shipment_id,
        sh.shipment_date,
        sh.expected_delivery as shipment_expected_delivery,
        sh.actual_delivery as shipment_actual_delivery,
        sh.status as shipment_status,
        f.forecast_demand
    from inventory as i
    left join suppliers as s
        on i.product_id = s.product_id
    left join purchase_orders as po
        on i.product_id = po.product_id
    left join shipments as sh
        on po.po_id = sh.po_id
    left join forecast as f
        on i.product_id = f.product_id

)

select * from joined
