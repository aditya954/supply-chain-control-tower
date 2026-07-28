{% snapshot snap_supplier %}

{{
    config(
        unique_key='supplier_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select * from {{ ref('stg_supplier') }}

{% endsnapshot %}
