with calendar as (

    select * from {{ ref('stg_calendar') }}

),

final as (

    select
        cast(date_key as number) as date_key,
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
        {{ generate_surrogate_key(['calendar_date']) }} as date_sk,
        {{ audit_columns() }}
    from calendar

)

select * from final
