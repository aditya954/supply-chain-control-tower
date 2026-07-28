{% macro audit_columns() %}
    current_timestamp() as dbt_loaded_at,
    '{{ invocation_id }}' as dbt_invocation_id,
    '{{ run_started_at }}' as dbt_run_started_at
{% endmacro %}
