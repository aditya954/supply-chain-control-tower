-- AI Supply Chain Control Tower — RAW tables (CT_* prefix)
-- Source data only — no business logic. Loaded from data/*.csv

USE ROLE TRANSFORMER;
USE DATABASE ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS CT_PRODUCTS (
    product_id       VARCHAR(10)   NOT NULL,
    product_name     VARCHAR(200)  NOT NULL,
    category         VARCHAR(100),
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS CT_WAREHOUSES (
    warehouse_id     VARCHAR(10)   NOT NULL,
    warehouse_name   VARCHAR(200)  NOT NULL,
    country          VARCHAR(10),
    capacity         NUMBER(18, 0),
    used_capacity    NUMBER(18, 0),
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS CT_SUPPLIERS (
    supplier_id      VARCHAR(10)   NOT NULL,
    supplier_name    VARCHAR(200)  NOT NULL,
    country          VARCHAR(10),
    lead_time_days   NUMBER(5, 0),
    otif_pct         NUMBER(5, 1),
    quality_pct      NUMBER(5, 1),
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS CT_INVENTORY (
    product_id       VARCHAR(10)   NOT NULL,
    warehouse_id     VARCHAR(10)   NOT NULL,
    snapshot_date    DATE          NOT NULL,
    stock_qty        NUMBER(18, 0) NOT NULL,
    reserved_qty     NUMBER(18, 0) NOT NULL,
    available_qty    NUMBER(18, 0) NOT NULL,
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS CT_DEMAND (
    product_id       VARCHAR(10)   NOT NULL,
    warehouse_id     VARCHAR(10)   NOT NULL,
    date             DATE          NOT NULL,
    actual_demand    NUMBER(18, 0),
    forecast_demand  NUMBER(18, 0),
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS CT_PURCHASE_ORDERS (
    po_id            VARCHAR(20)   NOT NULL,
    product_id       VARCHAR(10)   NOT NULL,
    supplier_id      VARCHAR(10)   NOT NULL,
    ordered_qty      NUMBER(18, 0) NOT NULL,
    received_qty     NUMBER(18, 0) NOT NULL,
    order_date       DATE          NOT NULL,
    expected_date    DATE,
    actual_date      DATE,
    status           VARCHAR(20)   NOT NULL,
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS CT_SHIPMENTS (
    shipment_id      VARCHAR(20)   NOT NULL,
    po_id            VARCHAR(20)   NOT NULL,
    ship_date        DATE,
    expected_delivery DATE,
    actual_delivery  DATE,
    status           VARCHAR(20)   NOT NULL,
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS CT_SALES_ORDERS (
    order_id         VARCHAR(20)   NOT NULL,
    product_id       VARCHAR(10)   NOT NULL,
    warehouse_id     VARCHAR(10)   NOT NULL,
    order_qty        NUMBER(18, 0) NOT NULL,
    promised_date    DATE,
    delivery_date    DATE,
    status           VARCHAR(20)   NOT NULL,
    _loaded_at       TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
