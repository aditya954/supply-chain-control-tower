with suppliers as (

    select * from {{ ref('stg_supplier') }}

),

performance as (

    select * from {{ ref('int_supplier_performance') }}

),

final as (

    select
        s.supplier_id,
        s.supplier_code,
        s.supplier_name,
        s.supplier_tier,
        s.country_code,
        s.city,
        s.contact_email,
        s.contact_phone,
        s.payment_terms,
        s.lead_time_days,
        s.is_active,
        s.created_at,
        s.updated_at,
        coalesce(p.on_time_delivery_pct, 0) as on_time_delivery_pct,
        coalesce(p.avg_delay_days, 0) as avg_delay_days,
        coalesce(p.avg_lead_time, s.lead_time_days) as avg_lead_time,
        coalesce(p.delivery_count, 0) as delivery_count,
        {{ audit_columns() }}
    from suppliers as s
    left join performance as p
        on s.supplier_id = p.supplier_id

)

select * from final
