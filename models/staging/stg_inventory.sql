with source as (

    select * from {{ ref('raw_inventory') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by inventory_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(inventory_id as number) as inventory_id,
        cast(material_id as number) as material_id,
        cast(warehouse_id as number) as warehouse_id,
        cast(on_hand_quantity as number) as on_hand_quantity,
        cast(reserved_quantity as number) as reserved_quantity,
        cast(available_quantity as number) as available_quantity,
        cast(reorder_point as number) as reorder_point,
        cast(safety_stock as number) as safety_stock,
        try_to_date(cast(last_movement_date as varchar)) as last_movement_date,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where inventory_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    inventory_id,
    material_id,
    warehouse_id,
    on_hand_quantity,
    reserved_quantity,
    available_quantity,
    reorder_point,
    safety_stock,
    last_movement_date,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
