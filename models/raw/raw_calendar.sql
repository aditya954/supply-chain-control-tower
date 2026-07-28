select *
from {{ source('raw_supply_chain', 'calendar') }}
