-- Critical suppliers should be flagged when OTD falls below threshold
select *
from {{ ref('mart_ct_supplier_health') }}
where supplier_id in ('S04', 'S08')
  and is_supplier_risk = false
