with source as (

    select * from {{ ref('raw_calendar') }}

),

deduplicated as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by date_key
                order by date_key desc
            ) as _dedup_row_num
        from source
    )
    where _dedup_row_num = 1

),

renamed as (

    select
        cast(date_key as number) as date_key,
        try_to_date(cast(calendar_date as varchar)) as calendar_date,
        cast(year as number) as year,
        cast(quarter as number) as quarter,
        cast(month as number) as month,
        trim(month_name) as month_name,
        cast(day_of_month as number) as day_of_month,
        cast(day_of_week as number) as day_of_week,
        trim(day_name) as day_name,
        cast(week_of_year as number) as week_of_year,
        upper(trim(coalesce(is_weekend, 'N'))) as is_weekend,
        upper(trim(coalesce(is_holiday, 'N'))) as is_holiday,
        cast(fiscal_year as number) as fiscal_year,
        cast(fiscal_quarter as number) as fiscal_quarter
    from deduplicated
    where date_key is not null

),

final as (

    select
        *,
        {{ audit_columns() }}
    from renamed

)

select
    date_key,
    calendar_date,
    year,
    quarter,
    month,
    month_name,
    day_of_month,
    day_of_week,
    day_name,
    week_of_year,
    is_weekend,
    is_holiday,
    fiscal_year,
    fiscal_quarter,
    dbt_loaded_at,
    dbt_invocation_id,
    dbt_run_started_at
from final
