with inventory as (

    select * from {{ ref('int_ct_inventory_position') }}

),

products as (

    select * from {{ ref('stg_ct_products') }}

),

warehouses as (

    select * from {{ ref('stg_ct_warehouses') }}

)

select
    p.product_id,
    p.product_name,
    p.category,
    w.warehouse_id,
    w.warehouse_name,
    w.country as warehouse_country,
    i.snapshot_date,
    i.stock_qty,
    i.reserved_qty,
    i.available_qty,
    i.avg_daily_demand_7d,
    i.avg_daily_demand_30d,
    i.days_of_supply,
    i.inventory_turnover_annualized,
    i.is_stockout_risk,
    i.is_excess_inventory,
    i.is_slow_moving,
    current_timestamp() as last_updated_at
from inventory as i
inner join products as p
    on i.product_id = p.product_id
inner join warehouses as w
    on i.warehouse_id = w.warehouse_id
