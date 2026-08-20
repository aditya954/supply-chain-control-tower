select * from {{ source('raw_dock_vision', 'dv_load_inspections') }}
