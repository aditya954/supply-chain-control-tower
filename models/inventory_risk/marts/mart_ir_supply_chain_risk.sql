with base as (

    select * from {{ ref('int_ir_supply_chain_risk') }}

),

excess_elsewhere as (

    select
        product_id,
        count(*) as warehouse_count,
        sum(case when stock_qty / nullif(daily_demand, 0) > 10 then 1 else 0 end) as excess_warehouse_count
    from {{ ref('stg_ir_inventory') }}
    group by 1

),

calculated as (

    select
        b.product_id,
        b.product_name,
        b.warehouse,
        b.stock_qty,
        b.daily_demand,
        round(b.stock_qty / nullif(b.daily_demand, 0), 2) as days_of_supply,
        b.daily_demand * b.lead_time_days as reorder_point,
        b.supplier_id,
        b.supplier_name,
        b.supplier_otd_pct,
        b.lead_time_days,
        b.po_id,
        b.po_status,
        b.shipment_id,
        b.shipment_status,
        b.forecast_demand,
        case
            when b.stock_qty / nullif(b.daily_demand, 0) < 1 then 'CRITICAL'
            when b.stock_qty / nullif(b.daily_demand, 0) < 2 then 'HIGH'
            else 'LOW'
        end as inventory_risk,
        case
            when b.supplier_otd_pct < 80 then 'HIGH'
            else 'LOW'
        end as supplier_risk,
        case
            when b.shipment_status = 'DELAYED' then 'HIGH'
            else 'LOW'
        end as shipment_risk,
        coalesce(e.excess_warehouse_count, 0) as excess_warehouse_count,
        b.snapshot_date
    from base as b
    left join excess_elsewhere as e
        on b.product_id = e.product_id

),

with_overall_risk as (

    select
        *,
        case
            when days_of_supply < 1 and shipment_status = 'DELAYED' then 'CRITICAL'
            when days_of_supply < 2 or supplier_otd_pct < 80 then 'HIGH'
            else 'LOW'
        end as overall_risk
    from calculated

),

final as (

    select
        product_id,
        product_name,
        warehouse,
        stock_qty,
        daily_demand,
        days_of_supply,
        reorder_point,
        supplier_id,
        supplier_name,
        supplier_otd_pct,
        lead_time_days,
        po_id,
        po_status,
        shipment_id,
        shipment_status,
        forecast_demand,
        inventory_risk,
        supplier_risk,
        shipment_risk,
        overall_risk,
        case
            when overall_risk = 'CRITICAL' and shipment_status = 'DELAYED'
                then 'EXPEDITE_REPLENISHMENT'
            when overall_risk = 'HIGH' and supplier_otd_pct < 80
                then 'REVIEW_SUPPLIER'
            when overall_risk = 'HIGH' and excess_warehouse_count > 0
                then 'CONSIDER_REALLOCATION'
            else 'MONITOR'
        end as recommended_action,
        snapshot_date
    from with_overall_risk

)

select * from final
