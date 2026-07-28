with source as (

    select * from {{ ref('raw_carrier') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by carrier_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(carrier_id as number) as carrier_id,
        trim(carrier_code) as carrier_code,
        trim(carrier_name) as carrier_name,
        trim(transport_mode) as transport_mode,
        trim(service_level) as service_level,
        upper(trim(country_code)) as country_code,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where carrier_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    carrier_id,
    carrier_code,
    carrier_name,
    transport_mode,
    service_level,
    country_code,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
