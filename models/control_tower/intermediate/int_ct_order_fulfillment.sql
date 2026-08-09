with sales_orders as (

    select * from {{ ref('stg_ct_sales_orders') }}
    where status != 'CANCELLED'

),

enriched as (

    select
        product_id,
        warehouse_id,
        order_id,
        order_qty,
        status,
        promised_date,
        delivery_date,
        case when status = 'BACKORDER' then 1 else 0 end as is_backorder,
        case
            when status in ('SHIPPED', 'DELIVERED') then 1
            else 0
        end as is_fulfilled,
        case
            when status in ('SHIPPED', 'DELIVERED')
                and delivery_date is not null
                and delivery_date <= promised_date then 1
            when status in ('SHIPPED', 'DELIVERED') then 0
            else null
        end as is_on_time_in_full
    from sales_orders

),

by_product_warehouse as (

    select
        product_id,
        warehouse_id,
        count(*) as total_order_count,
        sum(order_qty) as total_order_qty,
        sum(case when is_fulfilled = 1 then order_qty else 0 end) as fulfilled_qty,
        sum(is_backorder) as backorder_count,
        round(
            sum(case when is_fulfilled = 1 then order_qty else 0 end)
            / nullif(sum(order_qty), 0) * 100,
            2
        ) as fill_rate_pct,
        round(
            sum(is_backorder) / nullif(count(*), 0) * 100,
            2
        ) as backorder_rate_pct,
        round(
            avg(case when is_on_time_in_full = 1 then 100.0 when is_on_time_in_full = 0 then 0.0 end),
            2
        ) as otif_pct,
        sum(case when status in ('OPEN', 'CONFIRMED', 'BACKORDER') then order_qty else 0 end)
            as at_risk_customer_qty
    from enriched
    group by 1, 2

)

select
    *,
    round(
        at_risk_customer_qty / nullif(total_order_qty, 0) * 100,
        2
    ) as customer_impact_pct
from by_product_warehouse
