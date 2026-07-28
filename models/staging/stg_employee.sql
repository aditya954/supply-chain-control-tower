with source as (

    select * from {{ ref('raw_employee') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by employee_id
                order by updated_at desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(employee_id as number) as employee_id,
        trim(employee_code) as employee_code,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        lower(trim(email)) as email,
        trim(department) as department,
        cast(plant_id as number) as plant_id,
        try_to_date(cast(hire_date as varchar)) as hire_date,
        upper(trim(coalesce(is_active, 'N'))) as is_active,
        try_to_date(cast(created_at as varchar)) as created_at,
        try_to_date(cast(updated_at as varchar)) as updated_at
    from deduplicated
    where employee_id is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    employee_id,
    employee_code,
    first_name,
    last_name,
    email,
    department,
    plant_id,
    hire_date,
    is_active,
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
