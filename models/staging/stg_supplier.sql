with source as (

    select * from {{ ref('raw_supplier') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by supplier_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(supplier_id as number) as supplier_id,
        trim(supplier_code) as supplier_code,
        trim(supplier_name) as supplier_name,
        lower(trim(supplier_tier)) as supplier_tier,
        upper(trim(country_code)) as country_code,
        trim(city) as city,
        lower(trim(contact_email)) as contact_email,
        trim(contact_phone) as contact_phone,
        upper(trim(payment_terms)) as payment_terms,
        cast(lead_time_days as number) as lead_time_days,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where supplier_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    supplier_id,
    supplier_code,
    supplier_name,
    supplier_tier,
    country_code,
    city,
    contact_email,
    contact_phone,
    payment_terms,
    lead_time_days,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
