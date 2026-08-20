with base as (

    select * from {{ ref('int_dv_load_inspections') }}

)

select
    inspection_id,
    truck_id,
    trip_id,
    warehouse_id,
    route_id,
    dock_id,
    planned_pallets,
    planned_load_pct,
    estimated_load_pct,
    utilization_gap_pct,
    status,
    load_band,
    issue_codes,
    confidence,
    recommendation,
    supervisor_action,
    captured_at,
    inspection_date,
    round(estimated_load_pct - planned_load_pct, 1) as plan_vs_actual_delta_pct,
    case
        when status = 'OPTIMAL' then 'APPROVE_DEPARTURE'
        when status = 'UNDERLOADED' then 'TOP_UP_BEFORE_DEPARTURE'
        when status = 'UNSAFE' then 'RESTACK_BEFORE_DEPARTURE'
        else 'REVIEW_WEIGHT_LIMITS'
    end as recommended_action
from base
