{% macro safe_cast_timestamp(column_name) %}
    try_to_timestamp_ntz(cast({{ column_name }} as varchar))
{% endmacro %}
