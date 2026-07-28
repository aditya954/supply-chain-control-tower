{{
    config(
        materialized='incremental',
        unique_key='production_order_id',
        incremental_strategy='delete+insert'
    )
}}

with production_performance as (

    select * from {{ ref('int_production_performance') }}

    {% if is_incremental() %}
        where updated_at >= (
            select coalesce(max(updated_at), '1900-01-01'::date)
            from {{ this }}
        )
    {% endif %}

),

final as (

    select
        {{ generate_surrogate_key(['production_order_id']) }} as fact_production_key,
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
        efficiency_pct,
        scrap_rate_pct,
        avg_utilization_pct,
        created_at,
        updated_at,
        {{ audit_columns() }}
    from production_performance

)

select * from final
