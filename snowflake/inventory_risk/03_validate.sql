-- Inventory Risk Assistant — post-load validation
-- Run after scripts/load_inventory_risk_to_snowflake.py

USE DATABASE ANALYTICS;
USE SCHEMA RAW;

SELECT 'IR_INVENTORY' AS table_name, COUNT(*) AS row_count FROM IR_INVENTORY
UNION ALL SELECT 'IR_SUPPLIERS', COUNT(*) FROM IR_SUPPLIERS
UNION ALL SELECT 'IR_PURCHASE_ORDERS', COUNT(*) FROM IR_PURCHASE_ORDERS
UNION ALL SELECT 'IR_SHIPMENTS', COUNT(*) FROM IR_SHIPMENTS
UNION ALL SELECT 'IR_FORECAST', COUNT(*) FROM IR_FORECAST
ORDER BY table_name;

-- Headline demo: Coconut Body Wash
SELECT *
FROM IR_INVENTORY
WHERE product_id = 'P001';

SELECT
    i.product_name,
    i.warehouse,
    i.stock_qty,
    i.daily_demand,
    ROUND(i.stock_qty / NULLIF(i.daily_demand, 0), 2) AS days_of_supply,
    s.supplier_name,
    s.supplier_otd_pct,
    po.po_id,
    po.status AS po_status,
    sh.shipment_id,
    sh.status AS shipment_status
FROM IR_INVENTORY i
JOIN IR_SUPPLIERS s ON i.product_id = s.product_id
JOIN IR_PURCHASE_ORDERS po ON i.product_id = po.product_id
JOIN IR_SHIPMENTS sh ON po.po_id = sh.po_id
WHERE i.product_id = 'P001';
