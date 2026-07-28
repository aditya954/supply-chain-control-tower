{% macro coalesce_default(column_name, default_value) %}
    coalesce({{ column_name }}, {{ default_value }})
{% endmacro %}
