with inspections as (

    select * from {{ ref('stg_dv_load_inspections') }}

),

enriched as (

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
        status,
        issue_codes,
        confidence,
        recommendation,
        supervisor_action,
        captured_at,
        photo_path,
        greatest(planned_load_pct - estimated_load_pct, 0) as utilization_gap_pct,
        case
            when status = 'OPTIMAL' then 0
            when status = 'UNDERLOADED' then 1
            when status in ('UNSAFE', 'OVERLOADED') then 2
            else 0
        end as severity_rank,
        case
            when estimated_load_pct >= 90 then 'ON_TARGET'
            when estimated_load_pct >= 75 then 'BELOW_TARGET'
            else 'CRITICAL_UNDERLOAD'
        end as load_band,
        date_trunc('day', captured_at) as inspection_date
    from inspections

)

select * from enriched
