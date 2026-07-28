-- Singular test: quality scores must be between 80 and 100
select *
from {{ ref('fact_quality') }}
where quality_score < 80
   or quality_score > 100
