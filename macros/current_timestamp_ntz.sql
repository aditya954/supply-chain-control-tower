{% macro current_timestamp_ntz() %}
    cast(current_timestamp() as timestamp_ntz)
{% endmacro %}
