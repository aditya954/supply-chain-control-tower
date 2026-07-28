{{
    config(
        materialized='incremental',
        unique_key='shipment_id',
        incremental_strategy='delete+insert'
    )
}}

with shipment_delay as (

    select * from {{ ref('int_shipment_delay') }}

    {% if is_incremental() %}
        where updated_at >= (
            select coalesce(max(updated_at), '1900-01-01'::date)
            from {{ this }}
        )
    {% endif %}

),

final as (

    select
        {{ generate_surrogate_key(['shipment_id']) }} as fact_shipment_key,
        shipment_id,
        shipment_number,
        carrier_id,
        origin_warehouse_id,
        destination_customer_id,
        ship_date,
        expected_delivery_date,
        actual_delivery_date,
        shipment_status,
        weight_kg,
        freight_cost_usd,
        delay_days,
        transit_days,
        is_delayed,
        created_at,
        updated_at,
        {{ audit_columns() }}
    from shipment_delay

)

select * from final
