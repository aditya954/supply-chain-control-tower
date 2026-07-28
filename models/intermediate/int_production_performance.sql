with production_orders as (

    select * from {{ ref('stg_production_orders') }}

),

sensor_readings as (

    select * from {{ ref('stg_machine_sensor_readings') }}

),

order_sensor_utilization as (

    select
        po.production_order_id,
        round(avg(sr.utilization_pct), 2) as avg_utilization_pct
    from production_orders as po
    inner join sensor_readings as sr
        on po.machine_id = sr.machine_id
        and sr.reading_timestamp::date >= coalesce(po.actual_start_date, po.planned_start_date)
        and sr.reading_timestamp::date <= coalesce(po.actual_end_date, po.planned_end_date)
    group by po.production_order_id

),

enriched as (

    select
        po.production_order_id,
        po.production_order_number,
        po.plant_id,
        po.material_id,
        po.machine_id,
        po.planned_start_date,
        po.planned_end_date,
        po.actual_start_date,
        po.actual_end_date,
        po.planned_quantity,
        po.completed_quantity,
        po.scrap_quantity,
        po.production_status,
        po.created_at,
        po.updated_at,
        round(
            po.completed_quantity / nullif(po.planned_quantity, 0) * 100,
            2
        ) as efficiency_pct,
        round(
            po.scrap_quantity
            / nullif(po.completed_quantity + po.scrap_quantity, 0)
            * 100,
            2
        ) as scrap_rate_pct,
        coalesce(osu.avg_utilization_pct, 0) as avg_utilization_pct
    from production_orders as po
    left join order_sensor_utilization as osu
        on po.production_order_id = osu.production_order_id

)

select * from enriched
