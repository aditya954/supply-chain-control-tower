with source as (

    select * from {{ ref('raw_ct_products') }}

),

deduplicated as (

    {{ deduplicate('source', 'product_id', 'product_id') }}

),

renamed as (

    select
        trim(cast(product_id as varchar)) as product_id,
        trim(cast(product_name as varchar)) as product_name,
        trim(cast(category as varchar)) as category,
        try_to_timestamp_ntz(cast(_loaded_at as varchar)) as source_loaded_at,
        {{ audit_columns() }}
    from deduplicated
    where product_id is not null

)

select * from renamed
