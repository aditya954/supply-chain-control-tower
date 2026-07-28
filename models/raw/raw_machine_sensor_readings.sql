select *
from {{ source('raw_supply_chain', 'machine_sensor_readings') }}
