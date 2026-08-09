{% macro standardize_ct_po_status(column_name) %}
    upper(trim({{ column_name }}))
{% endmacro %}

{% macro standardize_ct_shipment_status(column_name) %}
    upper(trim(replace({{ column_name }}, ' ', '_')))
{% endmacro %}

{% macro standardize_ct_sales_status(column_name) %}
    upper(trim({{ column_name }}))
{% endmacro %}
