with source as (

    select * from {{ ref('raw_machine') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by machine_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(machine_id as number) as machine_id,
        trim(machine_code) as machine_code,
        trim(machine_name) as machine_name,
        cast(plant_id as number) as plant_id,
        trim(machine_type) as machine_type,
        cast(rated_capacity_per_hour as number) as rated_capacity_per_hour,
        try_to_date(cast(commissioned_date as varchar)) as commissioned_date,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where machine_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    machine_id,
    machine_code,
    machine_name,
    plant_id,
    machine_type,
    rated_capacity_per_hour,
    commissioned_date,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
