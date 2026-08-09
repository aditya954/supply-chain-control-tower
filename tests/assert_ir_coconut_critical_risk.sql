-- Coconut Body Wash must be CRITICAL with expedite action
select *
from {{ ref('mart_ir_supply_chain_risk') }}
where product_id = 'P001'
  and (
    overall_risk != 'CRITICAL'
    or recommended_action != 'EXPEDITE_REPLENISHMENT'
    or days_of_supply >= 1
  )
