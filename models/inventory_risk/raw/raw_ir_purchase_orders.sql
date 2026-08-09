select * from {{ source('raw_inventory_risk', 'ir_purchase_orders') }}
