-- Singular test: shipment delay days must be within business rules (0-15 days)
select *
from {{ ref('fact_shipments') }}
where delay_days < 0
   or delay_days > 15
