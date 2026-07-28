with source as (

    select * from {{ ref('raw_inventory_transactions') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by inventory_transaction_id
                order by created_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(inventory_transaction_id as number) as inventory_transaction_id,
        cast(inventory_id as number) as inventory_id,
        cast(material_id as number) as material_id,
        cast(warehouse_id as number) as warehouse_id,
        lower(trim(transaction_type)) as transaction_type,
        cast(transaction_quantity as number) as transaction_quantity,
        try_to_date(cast(transaction_date as varchar)) as transaction_date,
        trim(reference_document) as reference_document,
        try_to_timestamp_ntz(cast(created_at as varchar)) as created_at
    from deduplicated
    where inventory_transaction_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    inventory_transaction_id,
    inventory_id,
    material_id,
    warehouse_id,
    transaction_type,
    transaction_quantity,
    transaction_date,
    reference_document,
    created_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
