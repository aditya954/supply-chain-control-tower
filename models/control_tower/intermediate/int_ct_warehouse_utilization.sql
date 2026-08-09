with warehouses as (

    select * from {{ ref('stg_ct_warehouses') }}

),

inventory as (

    select
        warehouse_id,
        product_id,
        stock_qty
    from {{ ref('int_ct_inventory_position') }}

),

warehouse_totals as (

    select
        warehouse_id,
        sum(stock_qty) as total_stock_qty,
        count(distinct product_id) as product_count
    from inventory
    group by 1

),

product_share as (

    select
        i.warehouse_id,
        i.product_id,
        i.stock_qty,
        wt.total_stock_qty,
        round(i.stock_qty / nullif(wt.total_stock_qty, 0) * 100, 2) as inventory_concentration_pct
    from inventory as i
    inner join warehouse_totals as wt
        on i.warehouse_id = wt.warehouse_id

),

warehouse_metrics as (

    select
        w.warehouse_id,
        w.warehouse_name,
        w.country,
        w.capacity,
        w.used_capacity,
        round(w.used_capacity / nullif(w.capacity, 0) * 100, 2) as warehouse_utilization_pct,
        case
            when w.used_capacity / nullif(w.capacity, 0) > 0.9 then true
            else false
        end as is_capacity_risk,
        coalesce(wt.total_stock_qty, 0) as total_stock_qty,
        coalesce(wt.product_count, 0) as active_product_count
    from warehouses as w
    left join warehouse_totals as wt
        on w.warehouse_id = wt.warehouse_id

)

select
    wm.warehouse_id,
    wm.warehouse_name,
    wm.country,
    wm.capacity,
    wm.used_capacity,
    wm.warehouse_utilization_pct,
    wm.is_capacity_risk,
    wm.total_stock_qty,
    wm.active_product_count,
    ps.product_id,
    ps.stock_qty,
    ps.inventory_concentration_pct
from warehouse_metrics as wm
left join product_share as ps
    on wm.warehouse_id = ps.warehouse_id
