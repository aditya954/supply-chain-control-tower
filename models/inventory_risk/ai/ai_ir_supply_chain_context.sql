with mart as (

    select * from {{ ref('mart_ir_supply_chain_risk') }}

),

warehouse_names as (

    select column1 as warehouse_code, column2 as warehouse_name
    from (
        values
            ('LON', 'London'),
            ('NYC', 'New York'),
            ('CHI', 'Chicago'),
            ('AMS', 'Amsterdam'),
            ('SIN', 'Singapore')
    ) as wh (column1, column2)

),

enriched as (

    select
        m.*,
        coalesce(wh.warehouse_name, m.warehouse) as warehouse_display_name
    from mart as m
    left join warehouse_names as wh
        on m.warehouse = wh.warehouse_code

),

document_body as (

    select
        'DOC_' || product_id as document_id,
        product_id,
        warehouse,
        overall_risk as risk_level,
        concat(
            'Product: ', product_name, '\n',
            'Warehouse: ', warehouse_display_name, '\n',
            'Current Inventory: ', stock_qty, ' units\n',
            'Daily Demand: ', daily_demand, ' units\n',
            'Days of Supply: ', days_of_supply, '\n',
            'Reorder Point: ', reorder_point, ' units\n',
            'Supplier: ', supplier_name, ' (', supplier_id, ')\n',
            'Supplier OTD: ', supplier_otd_pct, '%\n',
            'Lead Time: ', lead_time_days, ' days\n',
            'Purchase Order: ', po_id, '\n',
            'PO Status: ', po_status, '\n',
            'Shipment: ', shipment_id, '\n',
            'Shipment Status: ', shipment_status, '\n',
            'Forecast Demand: ', forecast_demand, ' units\n',
            'Inventory Risk: ', inventory_risk, '\n',
            'Supplier Risk: ', supplier_risk, '\n',
            'Shipment Risk: ', shipment_risk, '\n',
            'Overall Risk: ', overall_risk, '\n',
            'Recommended Action: ', recommended_action
        ) as document_text,
        snapshot_date
    from enriched

),

final as (

    select
        document_id,
        product_id,
        warehouse,
        risk_level,
        document_text,
        sha2(document_text, 256) as document_hash,
        current_timestamp() as updated_at
    from document_body

)

select * from final
