with source as (

    select * from {{ ref('raw_ir_forecast') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by product_id, forecast_date
                order by _loaded_at desc nulls last
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        trim(cast(product_id as varchar)) as product_id,
        {{ safe_cast_date('forecast_date') }} as forecast_date,
        greatest(coalesce(cast(forecast_demand as number), 0), 0) as forecast_demand,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where product_id is not null

)

select * from renamed
