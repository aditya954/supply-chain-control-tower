with source as (

    select * from {{ ref('raw_production_orders') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by production_order_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(production_order_id as number) as production_order_id,
        trim(production_order_number) as production_order_number,
        cast(plant_id as number) as plant_id,
        cast(material_id as number) as material_id,
        cast(machine_id as number) as machine_id,
        try_to_date(cast(planned_start_date as varchar)) as planned_start_date,
        try_to_date(cast(planned_end_date as varchar)) as planned_end_date,
        try_to_date(cast(actual_start_date as varchar)) as actual_start_date,
        try_to_date(cast(actual_end_date as varchar)) as actual_end_date,
        cast(planned_quantity as number) as planned_quantity,
        cast(completed_quantity as number) as completed_quantity,
        cast(scrap_quantity as number) as scrap_quantity,
        lower(trim(production_status)) as production_status,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where production_order_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    production_order_id,
    production_order_number,
    plant_id,
    material_id,
    machine_id,
    planned_start_date,
    planned_end_date,
    actual_start_date,
    actual_end_date,
    planned_quantity,
    completed_quantity,
    scrap_quantity,
    production_status,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
