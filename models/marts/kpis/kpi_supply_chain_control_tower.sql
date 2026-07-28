with months as (

    select distinct
        to_char(calendar_date, 'YYYY-MM') as year_month,
        date_trunc('month', calendar_date)::date as month_start_date,
        last_day(calendar_date) as month_end_date,
        cast(year as number) as year,
        cast(month as number) as month
    from {{ ref('stg_calendar') }}

),

inventory_issues as (

    select
        to_char(it.transaction_date, 'YYYY-MM') as year_month,
        sum(it.transaction_quantity * m.unit_cost_usd) as cogs_value
    from {{ ref('stg_inventory_transactions') }} as it
    inner join {{ ref('stg_material') }} as m
        on it.material_id = m.material_id
    where it.transaction_type = 'issue'
    group by 1

),

inventory_snapshots as (

    select
        to_char(i.updated_at, 'YYYY-MM') as year_month,
        avg(i.inventory_value) as avg_inventory_value,
        avg(i.inventory_age_days) as inventory_age_days,
        avg(case when i.stockout_flag then 1.0 else 0.0 end) * 100 as stockout_rate
    from {{ ref('int_inventory_health') }} as i
    group by 1

),

supplier_monthly as (

    select
        to_char(sd.actual_delivery_date, 'YYYY-MM') as year_month,
        round(
            avg(case when sd.is_on_time = 'Y' then 100.0 else 0.0 end),
            2
        ) as supplier_on_time_delivery_pct,
        round(
            avg(datediff('day', po.order_date, sd.actual_delivery_date)),
            2
        ) as supplier_avg_lead_time_days
    from {{ ref('stg_supplier_deliveries') }} as sd
    inner join {{ ref('stg_purchase_orders') }} as po
        on sd.purchase_order_id = po.purchase_order_id
    where sd.actual_delivery_date is not null
    group by 1

),

production_monthly as (

    select
        to_char(coalesce(pp.actual_end_date, pp.planned_end_date), 'YYYY-MM') as year_month,
        round(avg(pp.efficiency_pct), 2) as production_efficiency_pct,
        round(avg(pp.scrap_rate_pct), 2) as scrap_rate_pct
    from {{ ref('int_production_performance') }} as pp
    group by 1

),

machine_utilization_monthly as (

    select
        to_char(sr.reading_timestamp, 'YYYY-MM') as year_month,
        round(avg(sr.utilization_pct), 2) as machine_utilization_pct
    from {{ ref('stg_machine_sensor_readings') }} as sr
    group by 1

),

quality_monthly as (

    select
        to_char(qm.inspection_date, 'YYYY-MM') as year_month,
        round(avg(qm.first_pass_yield_pct), 2) as first_pass_yield_pct,
        round(avg(qm.defect_rate_pct), 2) as quality_defect_rate
    from {{ ref('int_quality_metrics') }} as qm
    group by 1

),

shipment_monthly as (

    select
        to_char(sd.ship_date, 'YYYY-MM') as year_month,
        round(avg(case when sd.is_delayed then 100.0 else 0.0 end), 2) as shipment_delay_rate,
        round(avg(sd.transit_days), 2) as avg_transit_time_days
    from {{ ref('int_shipment_delay') }} as sd
    where sd.ship_date is not null
    group by 1

),

warranty_monthly as (

    select
        to_char(wc.claim_date, 'YYYY-MM') as year_month,
        count(*) as warranty_claim_count
    from {{ ref('stg_warranty_claims') }} as wc
    where wc.claim_date is not null
    group by 1

),

sales_monthly as (

    select
        to_char(so.order_date, 'YYYY-MM') as year_month,
        count(*) as sales_order_count
    from {{ ref('stg_sales_orders') }} as so
    where so.order_date is not null
    group by 1

),

joined as (

    select
        m.year_month,
        m.month_start_date,
        m.month_end_date,
        m.year,
        m.month,
        round(
            ii.cogs_value / nullif(inv.avg_inventory_value, 0),
            4
        ) as inventory_turnover,
        round(
            inv.avg_inventory_value
            / nullif(ii.cogs_value / 30.0, 0),
            2
        ) as days_of_inventory,
        round(inv.inventory_age_days, 2) as inventory_age_days,
        round(inv.stockout_rate, 2) as stockout_rate,
        sm.supplier_on_time_delivery_pct,
        sm.supplier_avg_lead_time_days,
        pm.production_efficiency_pct,
        mum.machine_utilization_pct,
        pm.scrap_rate_pct,
        qm.first_pass_yield_pct,
        shm.shipment_delay_rate,
        shm.avg_transit_time_days,
        qm.quality_defect_rate,
        round(
            wm.warranty_claim_count
            / nullif(sm_sales.sales_order_count, 0)
            * 100,
            2
        ) as warranty_claim_rate
    from months as m
    left join inventory_issues as ii
        on m.year_month = ii.year_month
    left join inventory_snapshots as inv
        on m.year_month = inv.year_month
    left join supplier_monthly as sm
        on m.year_month = sm.year_month
    left join production_monthly as pm
        on m.year_month = pm.year_month
    left join machine_utilization_monthly as mum
        on m.year_month = mum.year_month
    left join quality_monthly as qm
        on m.year_month = qm.year_month
    left join shipment_monthly as shm
        on m.year_month = shm.year_month
    left join warranty_monthly as wm
        on m.year_month = wm.year_month
    left join sales_monthly as sm_sales
        on m.year_month = sm_sales.year_month

),

final as (

    select
        {{ generate_surrogate_key(['year_month']) }} as kpi_key,
        year_month,
        month_start_date,
        month_end_date,
        year,
        month,
        coalesce(inventory_turnover, 0) as inventory_turnover,
        coalesce(days_of_inventory, 0) as days_of_inventory,
        coalesce(inventory_age_days, 0) as inventory_age_days,
        coalesce(stockout_rate, 0) as stockout_rate,
        coalesce(supplier_on_time_delivery_pct, 0) as supplier_on_time_delivery_pct,
        coalesce(supplier_avg_lead_time_days, 0) as supplier_avg_lead_time_days,
        coalesce(production_efficiency_pct, 0) as production_efficiency_pct,
        coalesce(machine_utilization_pct, 0) as machine_utilization_pct,
        coalesce(scrap_rate_pct, 0) as scrap_rate_pct,
        coalesce(first_pass_yield_pct, 0) as first_pass_yield_pct,
        coalesce(shipment_delay_rate, 0) as shipment_delay_rate,
        coalesce(avg_transit_time_days, 0) as avg_transit_time_days,
        coalesce(quality_defect_rate, 0) as quality_defect_rate,
        coalesce(warranty_claim_rate, 0) as warranty_claim_rate,
        {{ audit_columns() }}
    from joined
    where inventory_turnover is not null
        or days_of_inventory is not null
        or inventory_age_days is not null
        or stockout_rate is not null
        or supplier_on_time_delivery_pct is not null
        or supplier_avg_lead_time_days is not null
        or production_efficiency_pct is not null
        or machine_utilization_pct is not null
        or scrap_rate_pct is not null
        or first_pass_yield_pct is not null
        or shipment_delay_rate is not null
        or avg_transit_time_days is not null
        or quality_defect_rate is not null
        or warranty_claim_rate is not null

)

select * from final
