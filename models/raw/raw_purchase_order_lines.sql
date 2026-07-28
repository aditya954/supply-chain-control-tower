select *
from {{ source('raw_supply_chain', 'purchase_order_lines') }}
