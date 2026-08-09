with source as (

    select * from {{ ref('raw_ir_suppliers') }}

),

deduplicated as (

    {{ deduplicate('source', 'supplier_id', 'supplier_id') }}

),

renamed as (

    select
        trim(cast(supplier_id as varchar)) as supplier_id,
        trim(cast(supplier_name as varchar)) as supplier_name,
        trim(cast(product_id as varchar)) as product_id,
        coalesce(cast(lead_time_days as number), 0) as lead_time_days,
        coalesce(cast(supplier_otd_pct as number(5, 1)), 0) as supplier_otd_pct,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where supplier_id is not null

)

select * from renamed
