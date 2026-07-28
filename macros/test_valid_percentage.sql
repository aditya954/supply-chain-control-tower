{% test valid_percentage(model, column_name, min_value=0, max_value=200) %}
select *
from {{ model }}
where {{ column_name }} < {{ min_value }} or {{ column_name }} > {{ max_value }}
{% endtest %}
