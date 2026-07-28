{{
    config(
        materialized='incremental',
        unique_key='quality_inspection_id',
        incremental_strategy='delete+insert'
    )
}}

with quality_metrics as (

    select * from {{ ref('int_quality_metrics') }}

    {% if is_incremental() %}
        where updated_at >= (
            select coalesce(max(updated_at), '1900-01-01'::date)
            from {{ this }}
        )
    {% endif %}

),

final as (

    select
        {{ generate_surrogate_key(['quality_inspection_id']) }} as fact_quality_key,
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
        total_defect_quantity,
        defect_record_count,
        quality_score,
        inspection_result,
        first_pass_yield_pct,
        defect_rate_pct,
        created_at,
        updated_at,
        {{ audit_columns() }}
    from quality_metrics

)

select * from final
