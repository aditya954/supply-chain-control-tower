-- Inventory Risk Assistant — ensure required schemas exist
-- Reuses ANALYTICS database (no CREATE DATABASE)

USE ROLE TRANSFORMER;
USE DATABASE ANALYTICS;

CREATE SCHEMA IF NOT EXISTS RAW
  COMMENT = 'Source-aligned landing zone';

CREATE SCHEMA IF NOT EXISTS STAGING
  COMMENT = 'Cleaned and standardized data';

CREATE SCHEMA IF NOT EXISTS MART
  COMMENT = 'Analytics marts';

CREATE SCHEMA IF NOT EXISTS AI
  COMMENT = 'AI context, embeddings, and vector search';
