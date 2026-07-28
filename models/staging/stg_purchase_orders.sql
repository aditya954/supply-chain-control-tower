with source as (

    select * from {{ ref('raw_purchase_orders') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by purchase_order_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(purchase_order_id as number) as purchase_order_id,
        trim(po_number) as po_number,
        cast(supplier_id as number) as supplier_id,
        cast(plant_id as number) as plant_id,
        cast(buyer_employee_id as number) as buyer_employee_id,
        try_to_date(cast(order_date as varchar)) as order_date,
        try_to_date(cast(expected_delivery_date as varchar)) as expected_delivery_date,
        lower(trim(po_status)) as po_status,
        upper(trim(coalesce(currency_code, 'USD'))) as currency_code,
        cast(total_amount_usd as number(18, 2)) as total_amount_usd,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where purchase_order_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    purchase_order_id,
    po_number,
    supplier_id,
    plant_id,
    buyer_employee_id,
    order_date,
    expected_delivery_date,
    po_status,
    currency_code,
    total_amount_usd,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
