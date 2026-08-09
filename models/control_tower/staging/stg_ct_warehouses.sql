with source as (

    select * from {{ ref('raw_ct_warehouses') }}

),

deduplicated as (

    {{ deduplicate('source', 'warehouse_id', 'warehouse_id') }}

),

renamed as (

    select
        trim(cast(warehouse_id as varchar)) as warehouse_id,
        trim(cast(warehouse_name as varchar)) as warehouse_name,
        upper(trim(cast(country as varchar))) as country,
        coalesce(cast(capacity as number), 0) as capacity,
        coalesce(cast(used_capacity as number), 0) as used_capacity,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where warehouse_id is not null

)

select * from renamed
