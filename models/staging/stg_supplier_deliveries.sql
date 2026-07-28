with source as (

    select * from {{ ref('raw_supplier_deliveries') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by supplier_delivery_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(supplier_delivery_id as number) as supplier_delivery_id,
        cast(purchase_order_id as number) as purchase_order_id,
        cast(supplier_id as number) as supplier_id,
        cast(plant_id as number) as plant_id,
        trim(delivery_number) as delivery_number,
        try_to_date(cast(scheduled_delivery_date as varchar)) as scheduled_delivery_date,
        try_to_date(cast(actual_delivery_date as varchar)) as actual_delivery_date,
        cast(coalesce(delivery_delay_days, 0) as number) as delivery_delay_days,
        cast(delivered_quantity as number) as delivered_quantity,
        upper(trim(coalesce(is_on_time, 'N'))) as is_on_time,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where supplier_delivery_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    supplier_delivery_id,
    purchase_order_id,
    supplier_id,
    plant_id,
    delivery_number,
    scheduled_delivery_date,
    actual_delivery_date,
    delivery_delay_days,
    delivered_quantity,
    is_on_time,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
