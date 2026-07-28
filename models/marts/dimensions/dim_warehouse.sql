with warehouses as (

    select * from {{ ref('stg_warehouse') }}

),

plants as (

    select * from {{ ref('stg_plant') }}

),

final as (

    select
        w.warehouse_id,
        w.warehouse_code,
        w.warehouse_name,
        w.plant_id,
        w.warehouse_type,
        w.capacity_pallets,
        w.is_active as warehouse_is_active,
        w.created_at as warehouse_created_at,
        w.updated_at as warehouse_updated_at,
        p.plant_code,
        p.plant_name,
        p.region,
        p.country_code as plant_country_code,
        p.city as plant_city,
        p.capacity_units_per_day,
        p.is_active as plant_is_active,
        {{ audit_columns() }}
    from warehouses as w
    inner join plants as p
        on w.plant_id = p.plant_id

)

select * from final
