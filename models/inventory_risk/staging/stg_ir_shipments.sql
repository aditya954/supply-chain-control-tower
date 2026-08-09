with source as (

    select * from {{ ref('raw_ir_shipments') }}

),

deduplicated as (

    {{ deduplicate('source', 'shipment_id', 'shipment_date desc, _loaded_at desc') }}

),

renamed as (

    select
        trim(cast(shipment_id as varchar)) as shipment_id,
        trim(cast(po_id as varchar)) as po_id,
        {{ safe_cast_date('shipment_date') }} as shipment_date,
        {{ safe_cast_date('expected_delivery') }} as expected_delivery,
        {{ safe_cast_date('actual_delivery') }} as actual_delivery,
        upper(trim(cast(status as varchar))) as status,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where shipment_id is not null

)

select * from renamed
