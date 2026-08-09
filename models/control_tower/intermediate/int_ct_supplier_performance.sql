with suppliers as (

    select * from {{ ref('stg_ct_suppliers') }}

),

purchase_orders as (

    select * from {{ ref('stg_ct_purchase_orders') }}
    where status != 'CANCELLED'

),

po_metrics as (

    select
        po.supplier_id,
        count(*) as total_po_count,
        sum(po.ordered_qty) as total_ordered_qty,
        sum(po.received_qty) as total_received_qty,
        round(
            avg(
                case
                    when po.actual_date is not null
                        and po.actual_date <= po.expected_date then 100.0
                    when po.actual_date is not null then 0.0
                    else null
                end
            ),
            2
        ) as calculated_otd_pct,
        round(
            avg(
                case
                    when po.actual_date is not null
                        and po.actual_date <= po.expected_date
                        and po.received_qty >= po.ordered_qty then 100.0
                    when po.actual_date is not null then 0.0
                    else null
                end
            ),
            2
        ) as calculated_otif_pct,
        round(avg(datediff('day', po.order_date, po.actual_date)), 2) as avg_actual_lead_time_days,
        round(avg(datediff('day', po.expected_date, po.actual_date)), 2) as avg_delivery_delay_days
    from purchase_orders as po
    group by 1

),

final as (

    select
        s.supplier_id,
        s.supplier_name,
        s.country,
        s.lead_time_days as master_lead_time_days,
        s.otif_pct as master_otif_pct,
        s.quality_pct as master_quality_pct,
        coalesce(pm.calculated_otd_pct, s.otif_pct) as supplier_otd_pct,
        coalesce(pm.calculated_otif_pct, s.otif_pct) as supplier_otif_pct,
        coalesce(pm.avg_actual_lead_time_days, s.lead_time_days) as supplier_lead_time_days,
        coalesce(pm.avg_delivery_delay_days, 0) as avg_delivery_delay_days,
        coalesce(pm.total_po_count, 0) as total_po_count,
        case
            when coalesce(pm.calculated_otd_pct, s.otif_pct) < 80 then true
            when s.quality_pct < 90 then true
            when s.lead_time_days > 15 then true
            else false
        end as is_supplier_risk
    from suppliers as s
    left join po_metrics as pm
        on s.supplier_id = pm.supplier_id

)

select * from final
