with inventory as (

    select * from {{ ref('stg_inventory') }}

),

materials as (

    select * from {{ ref('stg_material') }}

),

enriched as (

    select
        i.inventory_id,
        i.material_id,
        i.warehouse_id,
        i.on_hand_quantity,
        i.reserved_quantity,
        i.available_quantity,
        i.reorder_point,
        i.safety_stock,
        i.last_movement_date,
        i.created_at,
        i.updated_at,
        m.material_code,
        m.material_name,
        m.material_type,
        m.material_category,
        m.unit_of_measure,
        m.unit_cost_usd,
        m.shelf_life_days,
        case
            when i.available_quantity = 0 then true
            else false
        end as stockout_flag,
        case
            when i.available_quantity < i.safety_stock then true
            else false
        end as below_safety_stock,
        round(i.available_quantity * m.unit_cost_usd, 2) as inventory_value,
        datediff('day', i.last_movement_date, current_date()) as inventory_age_days
    from inventory as i
    inner join materials as m
        on i.material_id = m.material_id

)

select * from enriched
