{% macro safe_cast_date(column_name) %}
    try_to_date(cast({{ column_name }} as varchar))
{% endmacro %}
