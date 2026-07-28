with machines as (

    select * from {{ ref('stg_machine') }}

),

machine_utilization as (

    select
        machine_id,
        round(avg(utilization_pct), 2) as avg_utilization_pct
    from {{ ref('stg_machine_sensor_readings') }}
    group by machine_id

),

final as (

    select
        m.machine_id,
        m.machine_code,
        m.machine_name,
        m.plant_id,
        m.machine_type,
        m.rated_capacity_per_hour,
        m.commissioned_date,
        m.is_active,
        m.created_at,
        m.updated_at,
        coalesce(mu.avg_utilization_pct, 0) as avg_utilization_pct,
        {{ audit_columns() }}
    from machines as m
    left join machine_utilization as mu
        on m.machine_id = mu.machine_id

)

select * from final
