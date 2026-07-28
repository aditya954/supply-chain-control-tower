with customers as (

    select * from {{ ref('stg_customer') }}

),

final as (

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
        {{ audit_columns() }}
    from customers

)

select * from final
