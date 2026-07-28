with source as (

    select * from {{ ref('raw_purchase_order_lines') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by purchase_order_line_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(purchase_order_line_id as number) as purchase_order_line_id,
        cast(purchase_order_id as number) as purchase_order_id,
        cast(line_number as number) as line_number,
        cast(material_id as number) as material_id,
        cast(ordered_quantity as number) as ordered_quantity,
        cast(received_quantity as number) as received_quantity,
        cast(unit_price_usd as number(18, 2)) as unit_price_usd,
        cast(line_amount_usd as number(18, 2)) as line_amount_usd,
        try_to_date(cast(requested_delivery_date as varchar)) as requested_delivery_date,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where purchase_order_line_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    purchase_order_line_id,
    purchase_order_id,
    line_number,
    material_id,
    ordered_quantity,
    received_quantity,
    unit_price_usd,
    line_amount_usd,
    requested_delivery_date,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
