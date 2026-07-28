with source as (

    select * from {{ ref('raw_warehouse') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by warehouse_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(warehouse_id as number) as warehouse_id,
        trim(warehouse_code) as warehouse_code,
        trim(warehouse_name) as warehouse_name,
        cast(plant_id as number) as plant_id,
        trim(warehouse_type) as warehouse_type,
        cast(capacity_pallets as number) as capacity_pallets,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where warehouse_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    warehouse_id,
    warehouse_code,
    warehouse_name,
    plant_id,
    warehouse_type,
    capacity_pallets,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
