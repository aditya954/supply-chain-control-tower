select *
from {{ source('raw_supply_chain', 'inventory_transactions') }}
