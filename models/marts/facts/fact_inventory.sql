{{
    config(
        materialized='incremental',
        unique_key='inventory_id',
        incremental_strategy='delete+insert'
    )
}}

with inventory_health as (

    select * from {{ ref('int_inventory_health') }}

    {% if is_incremental() %}
        where updated_at >= (
            select coalesce(max(updated_at), '1900-01-01'::date)
            from {{ this }}
        )
    {% endif %}

),

final as (

    select
        {{ generate_surrogate_key(['inventory_id']) }} as fact_inventory_key,
        inventory_id,
        material_id,
        warehouse_id,
        on_hand_quantity,
        reserved_quantity,
        available_quantity,
        reorder_point,
        safety_stock,
        last_movement_date,
        material_code,
        material_name,
        material_type,
        material_category,
        unit_of_measure,
        unit_cost_usd,
        shelf_life_days,
        stockout_flag,
        below_safety_stock,
        inventory_value,
        inventory_age_days,
        created_at,
        updated_at,
        {{ audit_columns() }}
    from inventory_health

)

select * from final
