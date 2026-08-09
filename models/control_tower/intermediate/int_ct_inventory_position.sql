with inventory as (

    select * from {{ ref('stg_ct_inventory') }}

),

latest_inventory as (

    select *
    from inventory
    qualify row_number() over (
        partition by product_id, warehouse_id
        order by snapshot_date desc, source_loaded_at desc
    ) = 1

),

demand_7d as (

    select
        product_id,
        warehouse_id,
        avg(actual_demand) as avg_daily_demand_7d
    from {{ ref('stg_ct_demand') }}
    where demand_record_type = 'ACTUAL'
      and demand_date >= dateadd('day', -7, current_date())
    group by 1, 2

),

demand_30d as (

    select
        product_id,
        warehouse_id,
        sum(actual_demand) as total_demand_30d,
        avg(actual_demand) as avg_daily_demand_30d
    from {{ ref('stg_ct_demand') }}
    where demand_record_type = 'ACTUAL'
      and demand_date >= dateadd('day', -30, current_date())
    group by 1, 2

),

enriched as (

    select
        li.product_id,
        li.warehouse_id,
        li.snapshot_date,
        li.stock_qty,
        li.reserved_qty,
        li.available_qty,
        coalesce(d7.avg_daily_demand_7d, 0) as avg_daily_demand_7d,
        coalesce(d30.avg_daily_demand_30d, 0) as avg_daily_demand_30d,
        coalesce(d30.total_demand_30d, 0) as total_demand_30d,
        case
            when coalesce(d7.avg_daily_demand_7d, 0) = 0 then null
            else round(li.available_qty / d7.avg_daily_demand_7d, 2)
        end as days_of_supply,
        case
            when coalesce(d30.avg_daily_demand_30d, 0) = 0 then null
            else round(
                (coalesce(d30.total_demand_30d, 0) / nullif(li.stock_qty, 0)) * 12,
                2
            )
        end as inventory_turnover_annualized,
        case
            when coalesce(d7.avg_daily_demand_7d, 0) = 0 then false
            when li.available_qty / d7.avg_daily_demand_7d < 3 then true
            else false
        end as is_stockout_risk,
        case
            when coalesce(d7.avg_daily_demand_7d, 0) = 0 then false
            when li.available_qty / d7.avg_daily_demand_7d > 45 then true
            else false
        end as is_excess_inventory,
        case
            when coalesce(d30.total_demand_30d, 0) < (li.stock_qty * 0.1) then true
            else false
        end as is_slow_moving
    from latest_inventory as li
    left join demand_7d as d7
        on li.product_id = d7.product_id
        and li.warehouse_id = d7.warehouse_id
    left join demand_30d as d30
        on li.product_id = d30.product_id
        and li.warehouse_id = d30.warehouse_id

)

select * from enriched
