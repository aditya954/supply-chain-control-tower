with source as (

    select * from {{ ref('raw_shipment_tracking') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by shipment_tracking_id
                order by created_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(shipment_tracking_id as number) as shipment_tracking_id,
        cast(shipment_id as number) as shipment_id,
        cast(tracking_event_sequence as number) as tracking_event_sequence,
        trim(event_type) as event_type,
        trim(event_location) as event_location,
        try_to_timestamp_ntz(cast(event_timestamp as varchar)) as event_timestamp,
        trim(event_description) as event_description,
        try_to_timestamp_ntz(cast(created_at as varchar)) as created_at
    from deduplicated
    where shipment_tracking_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    shipment_tracking_id,
    shipment_id,
    tracking_event_sequence,
    event_type,
    event_location,
    event_timestamp,
    event_description,
    created_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
