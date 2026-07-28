with deliveries as (

    select
        d.supplier_id,
        d.delivery_delay_days,
        d.is_on_time,
        d.scheduled_delivery_date,
        d.actual_delivery_date,
        po.order_date
    from {{ ref('stg_supplier_deliveries') }} as d
    inner join {{ ref('stg_purchase_orders') }} as po
        on d.purchase_order_id = po.purchase_order_id

),

supplier_metrics as (

    select
        d.supplier_id,
        round(
            avg(case when d.is_on_time = 'Y' then 100.0 else 0.0 end),
            2
        ) as on_time_delivery_pct,
        round(avg(d.delivery_delay_days), 2) as avg_delay_days,
        round(
            avg(datediff('day', d.order_date, d.actual_delivery_date)),
            2
        ) as avg_lead_time,
        count(*) as delivery_count
    from deliveries as d
    group by d.supplier_id

),

final as (

    select
        sm.supplier_id,
        sm.on_time_delivery_pct,
        sm.avg_delay_days,
        sm.avg_lead_time,
        sm.delivery_count,
        s.lead_time_days as master_lead_time_days,
        s.supplier_tier,
        s.is_active as supplier_is_active
    from supplier_metrics as sm
    inner join {{ ref('stg_supplier') }} as s
        on sm.supplier_id = s.supplier_id

)

select * from final
