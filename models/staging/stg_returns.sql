with source as (

    select * from {{ ref('raw_returns') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by return_id
                order by created_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(return_id as number) as return_id,
        trim(return_number) as return_number,
        cast(sales_order_id as number) as sales_order_id,
        cast(customer_id as number) as customer_id,
        cast(material_id as number) as material_id,
        cast(return_quantity as number) as return_quantity,
        trim(return_reason) as return_reason,
        try_to_date(cast(return_date as varchar)) as return_date,
        cast(return_amount_usd as number(18, 2)) as return_amount_usd,
        lower(trim(return_status)) as return_status,
        try_to_timestamp_ntz(cast(created_at as varchar)) as created_at
    from deduplicated
    where return_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    return_id,
    return_number,
    sales_order_id,
    customer_id,
    material_id,
    return_quantity,
    return_reason,
    return_date,
    return_amount_usd,
    return_status,
    created_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
