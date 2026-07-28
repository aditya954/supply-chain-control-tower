{% macro deduplicate(relation, partition_by, order_by='updated_at desc') %}
    select *
    from (
        select
            *,
            row_number() over (
                partition by {{ partition_by }}
                order by {{ order_by }}
            ) as _dedup_row_num
        from {{ relation }}
    )
    where _dedup_row_num = 1
{% endmacro %}
