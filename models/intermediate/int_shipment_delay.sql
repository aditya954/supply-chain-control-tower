with shipments as (

    select * from {{ ref('stg_shipments') }}

),

enriched as (

    select
        s.shipment_id,
        s.shipment_number,
        s.carrier_id,
        s.origin_warehouse_id,
        s.destination_customer_id,
        s.ship_date,
        s.expected_delivery_date,
        s.actual_delivery_date,
        s.shipment_status,
        s.weight_kg,
        s.freight_cost_usd,
        s.delay_days,
        s.created_at,
        s.updated_at,
        datediff(
            'day',
            s.ship_date,
            coalesce(s.actual_delivery_date, s.expected_delivery_date)
        ) as transit_days,
        case
            when s.delay_days > {{ var('supplier_otd_threshold_days') }}
                or s.shipment_status = 'delayed'
                then true
            else false
        end as is_delayed
    from shipments as s

)

select * from enriched
