-- DockVision — RAW tables (DV_* prefix)
-- Source data from mobile capture app + scripts/load_dock_vision_to_snowflake.py

USE ROLE TRANSFORMER;
USE DATABASE ANALYTICS;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS DV_LOAD_INSPECTIONS (
    inspection_id        VARCHAR(32)    NOT NULL,
    truck_id             VARCHAR(32)    NOT NULL,
    trip_id              VARCHAR(32)    NOT NULL,
    warehouse_id         VARCHAR(20)    NOT NULL,
    route_id             VARCHAR(32)    NOT NULL,
    dock_id              VARCHAR(10)    NOT NULL,
    planned_pallets      NUMBER(5, 0)   NOT NULL,
    planned_load_pct     NUMBER(5, 1)   NOT NULL,
    estimated_load_pct   NUMBER(5, 1)   NOT NULL,
    status               VARCHAR(20)    NOT NULL,
    issue_codes          VARCHAR(500),
    confidence           NUMBER(6, 3)   NOT NULL,
    recommendation       VARCHAR(1000),
    supervisor_action    VARCHAR(20),
    captured_at          TIMESTAMP_TZ   NOT NULL,
    photo_path           VARCHAR(500),
    synced_to_snowflake  BOOLEAN        DEFAULT TRUE,
    _loaded_at           TIMESTAMP_NTZ  DEFAULT CURRENT_TIMESTAMP()
);
