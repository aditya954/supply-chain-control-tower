with source as (

    select * from {{ ref('raw_ct_purchase_orders') }}

),

deduplicated as (

    {{ deduplicate('source', 'po_id', 'order_date desc, _loaded_at desc') }}

),

renamed as (

    select
        trim(cast(po_id as varchar)) as po_id,
        trim(cast(product_id as varchar)) as product_id,
        trim(cast(supplier_id as varchar)) as supplier_id,
        greatest(coalesce(cast(ordered_qty as number), 0), 0) as ordered_qty,
        greatest(coalesce(cast(received_qty as number), 0), 0) as received_qty,
        {{ safe_cast_date('order_date') }} as order_date,
        {{ safe_cast_date('expected_date') }} as expected_date,
        {{ safe_cast_date('actual_date') }} as actual_date,
        {{ standardize_ct_po_status('status') }} as status,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where po_id is not null

)

select * from renamed
