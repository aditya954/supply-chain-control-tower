select *
from {{ source('raw_supply_chain', 'warranty_claims') }}
