with source as (

    select * from {{ ref('raw_ct_suppliers') }}

),

deduplicated as (

    {{ deduplicate('source', 'supplier_id', 'supplier_id') }}

),

renamed as (

    select
        trim(cast(supplier_id as varchar)) as supplier_id,
        trim(cast(supplier_name as varchar)) as supplier_name,
        upper(trim(cast(country as varchar))) as country,
        coalesce(cast(lead_time_days as number), 0) as lead_time_days,
        coalesce(cast(otif_pct as number(5, 1)), 0) as otif_pct,
        coalesce(cast(quality_pct as number(5, 1)), 0) as quality_pct,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where supplier_id is not null

)

select * from renamed
