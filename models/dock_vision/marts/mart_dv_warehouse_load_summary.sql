with base as (

    select * from {{ ref('int_dv_load_inspections') }}

)

select
    warehouse_id,
    route_id,
    inspection_date,
    count(*) as inspection_count,
    round(avg(estimated_load_pct), 1) as avg_estimated_load_pct,
    round(avg(planned_load_pct), 1) as avg_planned_load_pct,
    round(avg(utilization_gap_pct), 1) as avg_utilization_gap_pct,
    sum(case when status = 'UNDERLOADED' then 1 else 0 end) as underloaded_count,
    sum(case when status = 'OPTIMAL' then 1 else 0 end) as optimal_count,
    sum(case when status in ('UNSAFE', 'OVERLOADED') then 1 else 0 end) as risk_count,
    round(
        100.0 * sum(case when status = 'OPTIMAL' then 1 else 0 end) / nullif(count(*), 0),
        1
    ) as optimal_rate_pct
from base
group by 1, 2, 3
