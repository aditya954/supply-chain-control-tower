with demand as (

    select * from {{ ref('stg_ct_demand') }}

),

historical as (

    select
        product_id,
        warehouse_id,
        demand_date,
        actual_demand,
        forecast_demand,
        abs(actual_demand - forecast_demand) as abs_error,
        actual_demand - forecast_demand as forecast_error
    from demand
    where demand_record_type = 'ACTUAL'
      and actual_demand is not null
      and forecast_demand is not null
      and actual_demand > 0

),

aggregated as (

    select
        product_id,
        warehouse_id,
        count(*) as demand_observation_days,
        round(avg(actual_demand), 2) as avg_actual_demand,
        round(avg(forecast_demand), 2) as avg_forecast_demand,
        round(avg(abs_error), 2) as mean_absolute_error,
        round(
            avg(abs_error / nullif(actual_demand, 0)) * 100,
            2
        ) as forecast_accuracy_pct,
        round(
            avg(forecast_error / nullif(actual_demand, 0)) * 100,
            2
        ) as forecast_bias_pct,
        round(stddev(actual_demand), 2) as demand_variance,
        round(stddev_pop(actual_demand), 2) as demand_stddev
    from historical
    group by 1, 2

),

forecast_forward as (

    select
        product_id,
        warehouse_id,
        round(avg(forecast_demand), 2) as forward_forecast_daily_demand
    from demand
    where demand_record_type = 'FORECAST'
      and demand_date between current_date() and dateadd('day', 30, current_date())
    group by 1, 2

),

final as (

    select
        coalesce(a.product_id, f.product_id) as product_id,
        coalesce(a.warehouse_id, f.warehouse_id) as warehouse_id,
        coalesce(a.demand_observation_days, 0) as demand_observation_days,
        a.avg_actual_demand,
        a.avg_forecast_demand,
        a.mean_absolute_error,
        a.forecast_accuracy_pct,
        a.forecast_bias_pct,
        a.demand_variance,
        a.demand_stddev,
        f.forward_forecast_daily_demand
    from aggregated as a
    full outer join forecast_forward as f
        on a.product_id = f.product_id
        and a.warehouse_id = f.warehouse_id

)

select * from final
