with source as (

    select * from {{ ref('raw_ct_sales_orders') }}

),

deduplicated as (

    {{ deduplicate('source', 'order_id', 'promised_date desc, _loaded_at desc') }}

),

renamed as (

    select
        trim(cast(order_id as varchar)) as order_id,
        trim(cast(product_id as varchar)) as product_id,
        trim(cast(warehouse_id as varchar)) as warehouse_id,
        greatest(coalesce(cast(order_qty as number), 0), 0) as order_qty,
        {{ safe_cast_date('promised_date') }} as promised_date,
        {{ safe_cast_date('delivery_date') }} as delivery_date,
        {{ standardize_ct_sales_status('status') }} as status,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where order_id is not null

)

select * from renamed
