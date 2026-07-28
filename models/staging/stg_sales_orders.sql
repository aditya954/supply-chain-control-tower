with source as (

    select * from {{ ref('raw_sales_orders') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by sales_order_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(sales_order_id as number) as sales_order_id,
        trim(sales_order_number) as sales_order_number,
        cast(customer_id as number) as customer_id,
        try_to_date(cast(order_date as varchar)) as order_date,
        try_to_date(cast(requested_delivery_date as varchar)) as requested_delivery_date,
        lower(trim(sales_order_status)) as sales_order_status,
        cast(total_amount_usd as number(18, 2)) as total_amount_usd,
        upper(trim(coalesce(currency_code, 'USD'))) as currency_code,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where sales_order_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    sales_order_id,
    sales_order_number,
    customer_id,
    order_date,
    requested_delivery_date,
    sales_order_status,
    total_amount_usd,
    currency_code,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
