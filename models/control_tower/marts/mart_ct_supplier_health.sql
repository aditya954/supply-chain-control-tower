select
    supplier_id,
    supplier_name,
    country,
    master_lead_time_days,
    master_otif_pct,
    master_quality_pct,
    supplier_otd_pct,
    supplier_otif_pct,
    supplier_lead_time_days,
    avg_delivery_delay_days,
    total_po_count,
    is_supplier_risk,
    current_timestamp() as last_updated_at
from {{ ref('int_ct_supplier_performance') }}
