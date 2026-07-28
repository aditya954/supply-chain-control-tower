with source as (

    select * from {{ ref('raw_material') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by material_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(material_id as number) as material_id,
        trim(material_code) as material_code,
        trim(material_name) as material_name,
        trim(material_type) as material_type,
        trim(material_category) as material_category,
        upper(trim(unit_of_measure)) as unit_of_measure,
        cast(unit_cost_usd as number(18, 2)) as unit_cost_usd,
        cast(shelf_life_days as number) as shelf_life_days,
        upper(trim(coalesce(is_hazardous, 'N'))) as is_hazardous,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where material_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    material_id,
    material_code,
    material_name,
    material_type,
    material_category,
    unit_of_measure,
    unit_cost_usd,
    shelf_life_days,
    is_hazardous,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
