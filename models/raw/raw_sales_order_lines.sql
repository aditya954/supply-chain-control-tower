select *
from {{ source('raw_supply_chain', 'sales_order_lines') }}
