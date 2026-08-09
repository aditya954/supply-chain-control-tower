-- Inventory Risk Assistant — RAW tables (IR_* prefix)
-- Source data only. Loaded from data/inventory_risk/*.csv

USE ROLE TRANSFORMER;
USE DATABASE ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS IR_INVENTORY (
    product_id      VARCHAR(10)   NOT NULL,
    product_name    VARCHAR(200)  NOT NULL,
    warehouse       VARCHAR(20)   NOT NULL,
    stock_qty       NUMBER(18, 0) NOT NULL,
    daily_demand    NUMBER(18, 0) NOT NULL,
    snapshot_date   DATE          NOT NULL,
    _loaded_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS IR_SUPPLIERS (
    supplier_id       VARCHAR(10)   NOT NULL,
    supplier_name     VARCHAR(200)  NOT NULL,
    product_id        VARCHAR(10)   NOT NULL,
    lead_time_days    NUMBER(5, 0)  NOT NULL,
    supplier_otd_pct  NUMBER(5, 1)  NOT NULL,
    _loaded_at        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS IR_PURCHASE_ORDERS (
    po_id           VARCHAR(20)   NOT NULL,
    product_id      VARCHAR(10)   NOT NULL,
    supplier_id     VARCHAR(10)   NOT NULL,
    ordered_qty     NUMBER(18, 0) NOT NULL,
    expected_date   DATE,
    status          VARCHAR(20)   NOT NULL,
    _loaded_at      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS IR_SHIPMENTS (
    shipment_id       VARCHAR(20)   NOT NULL,
    po_id             VARCHAR(20)   NOT NULL,
    shipment_date     DATE,
    expected_delivery DATE,
    actual_delivery   DATE,
    status            VARCHAR(20)   NOT NULL,
    _loaded_at        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS IR_FORECAST (
    product_id        VARCHAR(10)   NOT NULL,
    forecast_date     DATE          NOT NULL,
    forecast_demand   NUMBER(18, 0) NOT NULL,
    _loaded_at        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
