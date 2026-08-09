with source as (

    select * from {{ ref('raw_ir_inventory') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by product_id, warehouse, snapshot_date
                order by _loaded_at desc nulls last
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        trim(cast(product_id as varchar)) as product_id,
        trim(cast(product_name as varchar)) as product_name,
        upper(trim(cast(warehouse as varchar))) as warehouse,
        greatest(coalesce(cast(stock_qty as number), 0), 0) as stock_qty,
        greatest(coalesce(cast(daily_demand as number), 0), 0) as daily_demand,
        {{ safe_cast_date('snapshot_date') }} as snapshot_date,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where product_id is not null

)

select * from renamed
