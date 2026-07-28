-- Singular test: no negative inventory quantities in fact table
select *
from {{ ref('fact_inventory') }}
where on_hand_quantity < 0
   or available_quantity < 0
