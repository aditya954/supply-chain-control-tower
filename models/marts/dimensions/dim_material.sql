with materials as (

    select * from {{ ref('stg_material') }}

),

final as (

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
        {{ audit_columns() }}
    from materials

)

select * from final
