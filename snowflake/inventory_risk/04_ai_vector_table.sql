-- Inventory Risk Assistant — document embeddings storage
-- Populated incrementally by: python -m src.ai.embeddings

USE ROLE TRANSFORMER;
USE DATABASE ANALYTICS;
USE SCHEMA AI;

CREATE TABLE IF NOT EXISTS IR_DOCUMENT_EMBEDDINGS (
    document_id       VARCHAR(50)   NOT NULL,
    product_id        VARCHAR(20)   NOT NULL,
    warehouse         VARCHAR(20),
    risk_level        VARCHAR(20),
    document_text     VARCHAR(16777216),
    embedding         VECTOR(FLOAT, 768),
    embedding_model   VARCHAR(200)  NOT NULL,
    embedding_version VARCHAR(50)   NOT NULL,
    document_hash     VARCHAR(256)  NOT NULL,
    created_at        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at        TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (document_id)
);
