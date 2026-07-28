{{
    config(
        materialized='incremental',
        unique_key='purchase_order_id',
        incremental_strategy='delete+insert'
    )
}}

with purchase_orders as (

    select * from {{ ref('stg_purchase_orders') }}

    {% if is_incremental() %}
        where updated_at >= (
            select coalesce(max(updated_at), '1900-01-01'::date)
            from {{ this }}
        )
    {% endif %}

),

purchase_order_lines as (

    select
        purchase_order_id,
        count(*) as line_count,
        sum(ordered_quantity) as total_ordered_quantity,
        sum(received_quantity) as total_received_quantity,
        sum(line_amount_usd) as total_line_amount_usd,
        sum(case when received_quantity < ordered_quantity then 1 else 0 end) as open_line_count
    from {{ ref('stg_purchase_order_lines') }}
    group by purchase_order_id

),

final as (

    select
        {{ generate_surrogate_key(['po.purchase_order_id']) }} as fact_purchase_order_key,
        po.purchase_order_id,
        po.po_number,
        po.supplier_id,
        po.plant_id,
        po.buyer_employee_id,
        po.order_date,
        po.expected_delivery_date,
        po.po_status,
        po.currency_code,
        po.total_amount_usd,
        coalesce(pol.line_count, 0) as line_count,
        coalesce(pol.total_ordered_quantity, 0) as total_ordered_quantity,
        coalesce(pol.total_received_quantity, 0) as total_received_quantity,
        coalesce(pol.total_line_amount_usd, 0) as total_line_amount_usd,
        coalesce(pol.open_line_count, 0) as open_line_count,
        round(
            coalesce(pol.total_received_quantity, 0)
            / nullif(coalesce(pol.total_ordered_quantity, 0), 0)
            * 100,
            2
        ) as fulfillment_pct,
        po.created_at,
        po.updated_at,
        {{ audit_columns() }}
    from purchase_orders as po
    left join purchase_order_lines as pol
        on po.purchase_order_id = pol.purchase_order_id

)

select * from final
