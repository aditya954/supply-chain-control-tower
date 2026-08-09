-- AI Supply Chain Control Tower — schema layers
-- Extends existing RAW/STAGING/INTERMEDIATE/MART with SEMANTIC and AI.

USE ROLE TRANSFORMER;
USE DATABASE ANALYTICS;

CREATE SCHEMA IF NOT EXISTS RAW
  COMMENT = 'Source-aligned landing zone — no business logic';

CREATE SCHEMA IF NOT EXISTS STAGING
  COMMENT = 'Cleaned and standardized data';

CREATE SCHEMA IF NOT EXISTS INTERMEDIATE
  COMMENT = 'Modular business logic and joins';

CREATE SCHEMA IF NOT EXISTS MART
  COMMENT = 'Dimensional and fact models for analytics';

CREATE SCHEMA IF NOT EXISTS SEMANTIC
  COMMENT = 'Trusted business semantic layer for KPIs and AI';

CREATE SCHEMA IF NOT EXISTS AI
  COMMENT = 'AI data products — documents, embeddings, vector search';
