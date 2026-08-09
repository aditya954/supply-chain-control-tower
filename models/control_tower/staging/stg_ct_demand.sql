with source as (

    select * from {{ ref('raw_ct_demand') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by product_id, warehouse_id, date
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
        {{ safe_cast_date('date') }} as demand_date,
        cast(actual_demand as number) as actual_demand,
        coalesce(cast(forecast_demand as number), 0) as forecast_demand,
        case
            when actual_demand is null then 'FORECAST'
            else 'ACTUAL'
        end as demand_record_type,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where product_id is not null
      and warehouse_id is not null
      and demand_date is not null

)

select * from renamed
