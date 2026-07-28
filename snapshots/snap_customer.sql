{% snapshot snap_customer %}

{{
    config(
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select * from {{ ref('stg_customer') }}

{% endsnapshot %}
