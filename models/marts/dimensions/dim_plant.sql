with plants as (

    select * from {{ ref('stg_plant') }}

),

final as (

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
        {{ audit_columns() }}
    from plants

)

select * from final
