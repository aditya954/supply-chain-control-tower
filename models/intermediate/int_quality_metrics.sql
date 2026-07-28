with inspections as (

    select * from {{ ref('stg_quality_inspection') }}

),

defects as (

    select
        quality_inspection_id,
        sum(defect_quantity) as total_defect_quantity,
        count(*) as defect_record_count
    from {{ ref('stg_defects') }}
    group by quality_inspection_id

),

enriched as (

    select
        qi.quality_inspection_id,
        qi.inspection_number,
        qi.material_id,
        qi.plant_id,
        qi.production_order_id,
        qi.inspector_employee_id,
        qi.inspection_date,
        qi.inspected_quantity,
        qi.passed_quantity,
        qi.failed_quantity,
        qi.quality_score,
        qi.inspection_result,
        qi.created_at,
        qi.updated_at,
        coalesce(d.total_defect_quantity, qi.failed_quantity) as total_defect_quantity,
        coalesce(d.defect_record_count, 0) as defect_record_count,
        round(
            qi.passed_quantity / nullif(qi.inspected_quantity, 0) * 100,
            2
        ) as first_pass_yield_pct,
        least(
            round(
                coalesce(d.total_defect_quantity, qi.failed_quantity)
                / nullif(qi.inspected_quantity, 0)
                * 100,
                2
            ),
            100
        ) as defect_rate_pct
    from inspections as qi
    left join defects as d
        on qi.quality_inspection_id = d.quality_inspection_id

)

select * from enriched
