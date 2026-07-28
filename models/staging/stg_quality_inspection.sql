with source as (

    select * from {{ ref('raw_quality_inspection') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by quality_inspection_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(quality_inspection_id as number) as quality_inspection_id,
        trim(inspection_number) as inspection_number,
        cast(material_id as number) as material_id,
        cast(plant_id as number) as plant_id,
        cast(production_order_id as number) as production_order_id,
        cast(inspector_employee_id as number) as inspector_employee_id,
        try_to_date(cast(inspection_date as varchar)) as inspection_date,
        cast(inspected_quantity as number) as inspected_quantity,
        cast(passed_quantity as number) as passed_quantity,
        cast(failed_quantity as number) as failed_quantity,
        cast(quality_score as number(5, 2)) as quality_score,
        lower(trim(inspection_result)) as inspection_result,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where quality_inspection_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    quality_inspection_id,
    inspection_number,
    material_id,
    plant_id,
    production_order_id,
    inspector_employee_id,
    inspection_date,
    inspected_quantity,
    passed_quantity,
    failed_quantity,
    quality_score,
    inspection_result,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
