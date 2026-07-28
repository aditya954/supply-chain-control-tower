with source as (

    select * from {{ ref('raw_plant') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by plant_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(plant_id as number) as plant_id,
        trim(plant_code) as plant_code,
        trim(plant_name) as plant_name,
        upper(trim(region)) as region,
        upper(trim(country_code)) as country_code,
        trim(city) as city,
        cast(capacity_units_per_day as number) as capacity_units_per_day,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where plant_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    plant_id,
    plant_code,
    plant_name,
    region,
    country_code,
    city,
    capacity_units_per_day,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
