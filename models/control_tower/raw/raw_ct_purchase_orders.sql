select * from {{ source('raw_control_tower', 'ct_purchase_orders') }}
