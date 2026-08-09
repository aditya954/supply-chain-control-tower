with source as (

    select * from {{ ref('raw_ct_inventory') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by product_id, warehouse_id, snapshot_date
                order by _loaded_at desc nulls last
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        trim(cast(product_id as varchar)) as product_id,
        trim(cast(warehouse_id as varchar)) as warehouse_id,
        {{ safe_cast_date('snapshot_date') }} as snapshot_date,
        greatest(coalesce(cast(stock_qty as number), 0), 0) as stock_qty,
        greatest(coalesce(cast(reserved_qty as number), 0), 0) as reserved_qty,
        greatest(coalesce(cast(available_qty as number), 0), 0) as available_qty,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where product_id is not null
      and warehouse_id is not null
      and snapshot_date is not null

)

select * from renamed
