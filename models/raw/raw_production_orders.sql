select *
from {{ source('raw_supply_chain', 'production_orders') }}
