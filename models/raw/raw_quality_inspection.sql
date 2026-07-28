select *
from {{ source('raw_supply_chain', 'quality_inspection') }}
