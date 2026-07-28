{% snapshot snap_inventory %}

{{
    config(
        unique_key='inventory_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select * from {{ ref('stg_inventory') }}

{% endsnapshot %}
