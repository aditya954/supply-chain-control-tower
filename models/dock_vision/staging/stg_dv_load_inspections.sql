with source as (

    select * from {{ ref('raw_dv_load_inspections') }}

),

deduplicated as (

    {{ deduplicate('source', 'inspection_id', 'captured_at desc, _loaded_at desc') }}

),

renamed as (

    select
        trim(cast(inspection_id as varchar)) as inspection_id,
        trim(cast(truck_id as varchar)) as truck_id,
        trim(cast(trip_id as varchar)) as trip_id,
        upper(trim(cast(warehouse_id as varchar))) as warehouse_id,
        upper(trim(cast(route_id as varchar))) as route_id,
        upper(trim(cast(dock_id as varchar))) as dock_id,
        try_to_number(cast(planned_pallets as varchar)) as planned_pallets,
        try_to_number(cast(planned_load_pct as varchar)) as planned_load_pct,
        try_to_number(cast(estimated_load_pct as varchar)) as estimated_load_pct,
        upper(trim(cast(status as varchar))) as status,
        nullif(trim(cast(issue_codes as varchar)), '') as issue_codes,
        try_to_number(cast(confidence as varchar)) as confidence,
        trim(cast(recommendation as varchar)) as recommendation,
        upper(trim(cast(supervisor_action as varchar))) as supervisor_action,
        try_to_timestamp_tz(cast(captured_at as varchar)) as captured_at,
        trim(cast(photo_path as varchar)) as photo_path,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where inspection_id is not null

)

select * from renamed
