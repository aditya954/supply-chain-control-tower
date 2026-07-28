select *
from {{ source('raw_supply_chain', 'shipment_tracking') }}
