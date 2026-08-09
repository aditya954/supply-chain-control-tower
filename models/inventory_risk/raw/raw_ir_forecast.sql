select * from {{ source('raw_inventory_risk', 'ir_forecast') }}
