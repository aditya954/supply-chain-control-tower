{% docs __supply_chain_overview__ %}

# Enterprise Supply Chain Control Tower

This dbt project implements a Fortune 500-grade supply chain analytics platform
for automotive manufacturing. It ingests ERP, MES, TMS, and QMS data into
Snowflake and produces dimensional models, incremental facts, KPIs, and
slowly-changing dimension snapshots.

## Data Domains

- **Procurement**: Purchase orders, supplier deliveries, supplier performance
- **Inventory**: Stock positions, transactions, health metrics
- **Production**: Production orders, machine sensors, efficiency
- **Logistics**: Shipments, tracking events, transit times
- **Quality**: Inspections, defects, first-pass yield
- **Sales & Returns**: Sales orders, returns, warranty claims

{% enddocs %}
