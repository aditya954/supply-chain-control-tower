with source as (

    select * from {{ ref('raw_shipments') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by shipment_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(shipment_id as number) as shipment_id,
        trim(shipment_number) as shipment_number,
        cast(carrier_id as number) as carrier_id,
        cast(origin_warehouse_id as number) as origin_warehouse_id,
        cast(destination_customer_id as number) as destination_customer_id,
        try_to_date(cast(ship_date as varchar)) as ship_date,
        try_to_date(cast(expected_delivery_date as varchar)) as expected_delivery_date,
        try_to_date(cast(actual_delivery_date as varchar)) as actual_delivery_date,
        lower(trim(shipment_status)) as shipment_status,
        cast(weight_kg as number(18, 2)) as weight_kg,
        cast(freight_cost_usd as number(18, 2)) as freight_cost_usd,
        cast(coalesce(delay_days, 0) as number) as delay_days,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where shipment_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    shipment_id,
    shipment_number,
    carrier_id,
    origin_warehouse_id,
    destination_customer_id,
    ship_date,
    expected_delivery_date,
    actual_delivery_date,
    shipment_status,
    weight_kg,
    freight_cost_usd,
    delay_days,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
