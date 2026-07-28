{{
    config(
        materialized='table'
    )
}}

with supplier_performance as (

    select * from {{ ref('int_supplier_performance') }}

),

final as (

    select
        {{ generate_surrogate_key(['supplier_id']) }} as fact_supplier_performance_key,
        supplier_id,
        on_time_delivery_pct,
        avg_delay_days,
        avg_lead_time,
        delivery_count,
        master_lead_time_days,
        supplier_tier,
        supplier_is_active,
        {{ audit_columns() }}
    from supplier_performance

)

select * from final
