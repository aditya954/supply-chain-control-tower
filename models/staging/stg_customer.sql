with source as (

    select * from {{ ref('raw_customer') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by customer_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(customer_id as number) as customer_id,
        trim(customer_code) as customer_code,
        trim(customer_name) as customer_name,
        trim(customer_segment) as customer_segment,
        upper(trim(country_code)) as country_code,
        trim(city) as city,
        cast(credit_limit_usd as number(18, 2)) as credit_limit_usd,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where customer_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    customer_id,
    customer_code,
    customer_name,
    customer_segment,
    country_code,
    city,
    credit_limit_usd,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
