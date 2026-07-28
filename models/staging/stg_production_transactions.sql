with source as (

    select * from {{ ref('raw_production_transactions') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by production_transaction_id
                order by created_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(production_transaction_id as number) as production_transaction_id,
        cast(production_order_id as number) as production_order_id,
        cast(plant_id as number) as plant_id,
        cast(machine_id as number) as machine_id,
        cast(material_id as number) as material_id,
        lower(trim(transaction_type)) as transaction_type,
        cast(transaction_quantity as number) as transaction_quantity,
        try_to_date(cast(transaction_date as varchar)) as transaction_date,
        try_to_timestamp_ntz(cast(created_at as varchar)) as created_at
    from deduplicated
    where production_transaction_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    production_transaction_id,
    production_order_id,
    plant_id,
    machine_id,
    material_id,
    transaction_type,
    transaction_quantity,
    transaction_date,
    created_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
