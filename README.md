# My First dbt Project

This project turns sample customer data into a dbt model.

## Project files

```
models/
  customers.sql       # your first model
seeds/
  raw_customers.csv   # sample data
```

## Start here

Configure the `snowflake_dbt_starter` profile in your `profiles.yml`, then run:

```bash
dbt seed
dbt build
```

To run only your model, use:

```bash
dbt run --select customers
```
