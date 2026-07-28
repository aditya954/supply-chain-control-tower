with source as (

    select * from {{ ref('raw_machine_sensor_readings') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by sensor_reading_id
                order by created_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(sensor_reading_id as number) as sensor_reading_id,
        cast(machine_id as number) as machine_id,
        cast(plant_id as number) as plant_id,
        try_to_timestamp_ntz(cast(reading_timestamp as varchar)) as reading_timestamp,
        cast(temperature_celsius as number(10, 2)) as temperature_celsius,
        cast(vibration_mm_s as number(10, 3)) as vibration_mm_s,
        cast(utilization_pct as number(5, 2)) as utilization_pct,
        trim(coalesce(error_code, '')) as error_code,
        try_to_timestamp_ntz(cast(created_at as varchar)) as created_at
    from deduplicated
    where sensor_reading_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    sensor_reading_id,
    machine_id,
    plant_id,
    reading_timestamp,
    temperature_celsius,
    vibration_mm_s,
    utilization_pct,
    error_code,
    created_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
