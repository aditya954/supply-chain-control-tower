-- AI Supply Chain Control Tower — internal stage for CSV ingestion
-- Local loads use write_pandas — stage supports future COPY INTO workflows

USE ROLE TRANSFORMER;
USE DATABASE ANALYTICS;
USE SCHEMA RAW;

CREATE STAGE IF NOT EXISTS CT_CSV_STAGE
  COMMENT = 'Internal stage for Control Tower CSV files'
  FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('', 'NULL', 'null')
    EMPTY_FIELD_AS_NULL = TRUE
    TRIM_SPACE = TRUE
  );

CREATE FILE FORMAT IF NOT EXISTS CT_CSV_FORMAT
  TYPE = 'CSV'
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  SKIP_HEADER = 1
  NULL_IF = ('', 'NULL', 'null')
  EMPTY_FIELD_AS_NULL = TRUE
  TRIM_SPACE = TRUE;
