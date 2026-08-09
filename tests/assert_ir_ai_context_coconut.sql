-- AI context for Coconut Body Wash must exist and mention CRITICAL risk
select *
from {{ ref('ai_ir_supply_chain_context') }}
where product_id = 'P001'
  and (
    risk_level != 'CRITICAL'
    or document_text is null
    or document_hash is null
    or document_text not ilike '%Coconut Body Wash%'
    or document_text not ilike '%EXPEDITE_REPLENISHMENT%'
  )
