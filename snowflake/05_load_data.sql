-- AI Supply Chain Control Tower — validation queries after load
-- Run after scripts/load_control_tower_to_snowflake.py

USE DATABASE ANALYTICS;
USE SCHEMA RAW;

-- Row counts
SELECT 'CT_PRODUCTS' AS table_name, COUNT(*) AS row_count FROM CT_PRODUCTS
UNION ALL SELECT 'CT_WAREHOUSES', COUNT(*) FROM CT_WAREHOUSES
UNION ALL SELECT 'CT_SUPPLIERS', COUNT(*) FROM CT_SUPPLIERS
UNION ALL SELECT 'CT_INVENTORY', COUNT(*) FROM CT_INVENTORY
UNION ALL SELECT 'CT_DEMAND', COUNT(*) FROM CT_DEMAND
UNION ALL SELECT 'CT_PURCHASE_ORDERS', COUNT(*) FROM CT_PURCHASE_ORDERS
UNION ALL SELECT 'CT_SHIPMENTS', COUNT(*) FROM CT_SHIPMENTS
UNION ALL SELECT 'CT_SALES_ORDERS', COUNT(*) FROM CT_SALES_ORDERS
ORDER BY table_name;

-- Referential integrity spot checks
SELECT COUNT(*) AS orphan_inventory_products
FROM CT_INVENTORY i
LEFT JOIN CT_PRODUCTS p ON i.product_id = p.product_id
WHERE p.product_id IS NULL;

SELECT COUNT(*) AS orphan_po_suppliers
FROM CT_PURCHASE_ORDERS po
LEFT JOIN CT_SUPPLIERS s ON po.supplier_id = s.supplier_id
WHERE s.supplier_id IS NULL;

-- Critical scenario: Coconut at London
SELECT
    p.product_name,
    w.warehouse_name,
    i.available_qty,
    i.stock_qty,
    i.snapshot_date
FROM CT_INVENTORY i
JOIN CT_PRODUCTS p ON i.product_id = p.product_id
JOIN CT_WAREHOUSES w ON i.warehouse_id = w.warehouse_id
WHERE p.product_id = 'P001' AND w.warehouse_id = 'W01';

-- Delayed shipments for critical products
SELECT
    p.product_name,
    s.shipment_id,
    s.status,
    DATEDIFF('day', s.expected_delivery, CURRENT_DATE()) AS days_past_expected
FROM CT_SHIPMENTS s
JOIN CT_PURCHASE_ORDERS po ON s.po_id = po.po_id
JOIN CT_PRODUCTS p ON po.product_id = p.product_id
WHERE s.status = 'DELAYED'
  AND p.product_id IN ('P001', 'P004', 'P011', 'P028')
LIMIT 20;
