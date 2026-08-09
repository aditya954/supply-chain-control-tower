with inventory as (

    select * from {{ ref('int_ct_inventory_position') }}

),

demand as (

    select * from {{ ref('int_ct_demand_metrics') }}

),

fulfillment as (

    select * from {{ ref('int_ct_order_fulfillment') }}

),

warehouse as (

    select
        warehouse_id,
        product_id,
        warehouse_utilization_pct,
        is_capacity_risk,
        inventory_concentration_pct
    from {{ ref('int_ct_warehouse_utilization') }}
    where product_id is not null

),

supplier_product as (

    select
        po.product_id,
        po.supplier_id,
        sp.supplier_name,
        sp.supplier_otd_pct,
        sp.supplier_otif_pct,
        sp.supplier_lead_time_days,
        sp.is_supplier_risk
    from {{ ref('stg_ct_purchase_orders') }} as po
    inner join {{ ref('int_ct_supplier_performance') }} as sp
        on po.supplier_id = sp.supplier_id
    qualify row_number() over (
        partition by po.product_id
        order by po.order_date desc
    ) = 1

),

shipment as (

    select
        product_id,
        supplier_id,
        shipment_delay_rate_pct,
        avg_delivery_delay_days,
        on_time_shipment_rate_pct
    from {{ ref('int_ct_shipment_performance') }}

),

base as (

    select
        i.product_id,
        i.warehouse_id,
        sp.supplier_id,
        sp.supplier_name,
        i.available_qty,
        i.avg_daily_demand_7d as daily_demand,
        i.days_of_supply,
        i.is_stockout_risk,
        i.is_excess_inventory,
        i.is_slow_moving,
        d.forecast_accuracy_pct,
        d.forecast_bias_pct,
        d.forward_forecast_daily_demand,
        sp.supplier_otd_pct,
        sp.supplier_otif_pct,
        sp.is_supplier_risk,
        sh.shipment_delay_rate_pct,
        sh.avg_delivery_delay_days,
        f.fill_rate_pct,
        f.backorder_rate_pct,
        f.otif_pct,
        f.customer_impact_pct,
        w.warehouse_utilization_pct,
        w.is_capacity_risk,
        case when i.is_stockout_risk then 1 else 0 end
        + case when sp.is_supplier_risk then 1 else 0 end
        + case when coalesce(sh.shipment_delay_rate_pct, 0) > 25 then 1 else 0 end
        + case when coalesce(f.backorder_rate_pct, 0) > 20 then 1 else 0 end
        + case when w.is_capacity_risk then 1 else 0 end as risk_signal_count
    from inventory as i
    left join demand as d
        on i.product_id = d.product_id
        and i.warehouse_id = d.warehouse_id
    left join fulfillment as f
        on i.product_id = f.product_id
        and i.warehouse_id = f.warehouse_id
    left join warehouse as w
        on i.product_id = w.product_id
        and i.warehouse_id = w.warehouse_id
    left join supplier_product as sp
        on i.product_id = sp.product_id
    left join shipment as sh
        on i.product_id = sh.product_id
        and sp.supplier_id = sh.supplier_id

)

select * from base
