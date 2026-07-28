with source as (

    select * from {{ ref('raw_warranty_claims') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by warranty_claim_id
                order by created_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(warranty_claim_id as number) as warranty_claim_id,
        trim(claim_number) as claim_number,
        cast(customer_id as number) as customer_id,
        cast(material_id as number) as material_id,
        cast(sales_order_id as number) as sales_order_id,
        trim(warranty_type) as warranty_type,
        try_to_date(cast(claim_date as varchar)) as claim_date,
        cast(claim_amount_usd as number(18, 2)) as claim_amount_usd,
        lower(trim(claim_status)) as claim_status,
        cast(mileage_at_claim as number) as mileage_at_claim,
        try_to_timestamp_ntz(cast(created_at as varchar)) as created_at
    from deduplicated
    where warranty_claim_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    warranty_claim_id,
    claim_number,
    customer_id,
    material_id,
    sales_order_id,
    warranty_type,
    claim_date,
    claim_amount_usd,
    claim_status,
    mileage_at_claim,
    created_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
