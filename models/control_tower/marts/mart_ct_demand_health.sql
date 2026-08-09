with demand as (

    select * from {{ ref('int_ct_demand_metrics') }}

),

products as (

    select * from {{ ref('stg_ct_products') }}

),

warehouses as (

    select * from {{ ref('stg_ct_warehouses') }}

)

select
    d.product_id,
    p.product_name,
    d.warehouse_id,
    w.warehouse_name,
    d.demand_observation_days,
    d.avg_actual_demand,
    d.avg_forecast_demand,
    d.mean_absolute_error,
    d.forecast_accuracy_pct,
    d.forecast_bias_pct,
    d.demand_variance,
    d.demand_stddev,
    d.forward_forecast_daily_demand,
    current_timestamp() as last_updated_at
from demand as d
inner join products as p
    on d.product_id = p.product_id
inner join warehouses as w
    on d.warehouse_id = w.warehouse_id
