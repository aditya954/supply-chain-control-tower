with shipments as (

    select
        s.*,
        po.product_id,
        po.supplier_id
    from {{ ref('stg_ct_shipments') }} as s
    inner join {{ ref('stg_ct_purchase_orders') }} as po
        on s.po_id = po.po_id
    where s.status != 'CANCELLED'

),

shipment_detail as (

    select
        shipment_id,
        po_id,
        product_id,
        supplier_id,
        status,
        ship_date,
        expected_delivery,
        actual_delivery,
        case
            when status = 'DELIVERED'
                and actual_delivery <= expected_delivery then 1
            when status = 'DELIVERED' then 0
            else null
        end as is_on_time,
        case
            when actual_delivery is not null and expected_delivery is not null
                then datediff('day', expected_delivery, actual_delivery)
            when status = 'DELAYED' and expected_delivery is not null
                then datediff('day', expected_delivery, current_date())
            else null
        end as delivery_delay_days
    from shipments

),

by_product_supplier as (

    select
        product_id,
        supplier_id,
        count(*) as shipment_count,
        sum(case when status = 'DELAYED' then 1 else 0 end) as delayed_shipment_count,
        round(
            sum(case when status = 'DELAYED' then 1 else 0 end)
            / nullif(count(*), 0) * 100,
            2
        ) as shipment_delay_rate_pct,
        round(avg(case when is_on_time = 1 then 100.0 when is_on_time = 0 then 0.0 end), 2)
            as on_time_shipment_rate_pct,
        round(avg(delivery_delay_days), 2) as avg_delivery_delay_days
    from shipment_detail
    group by 1, 2

),

by_supplier as (

    select
        supplier_id,
        count(*) as shipment_count,
        round(
            sum(case when status = 'DELAYED' then 1 else 0 end)
            / nullif(count(*), 0) * 100,
            2
        ) as shipment_delay_rate_pct,
        round(avg(case when is_on_time = 1 then 100.0 when is_on_time = 0 then 0.0 end), 2)
            as on_time_shipment_rate_pct,
        round(avg(delivery_delay_days), 2) as avg_delivery_delay_days
    from shipment_detail
    group by 1

)

select
    bps.product_id,
    bps.supplier_id,
    bps.shipment_count,
    bps.delayed_shipment_count,
    bps.shipment_delay_rate_pct,
    bps.on_time_shipment_rate_pct,
    bps.avg_delivery_delay_days,
    bs.shipment_delay_rate_pct as supplier_shipment_delay_rate_pct,
    bs.on_time_shipment_rate_pct as supplier_on_time_shipment_rate_pct
from by_product_supplier as bps
left join by_supplier as bs
    on bps.supplier_id = bs.supplier_id
