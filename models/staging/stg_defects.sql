with source as (

    select * from {{ ref('raw_defects') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by defect_id
                order by created_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(defect_id as number) as defect_id,
        cast(quality_inspection_id as number) as quality_inspection_id,
        cast(material_id as number) as material_id,
        cast(plant_id as number) as plant_id,
        trim(defect_type) as defect_type,
        cast(defect_quantity as number) as defect_quantity,
        lower(trim(severity)) as severity,
        try_to_date(cast(defect_date as varchar)) as defect_date,
        trim(root_cause) as root_cause,
        try_to_timestamp_ntz(cast(created_at as varchar)) as created_at
    from deduplicated
    where defect_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    defect_id,
    quality_inspection_id,
    material_id,
    plant_id,
    defect_type,
    defect_quantity,
    severity,
    defect_date,
    root_cause,
    created_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
