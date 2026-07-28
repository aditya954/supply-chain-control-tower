{% snapshot snap_material %}

{{
    config(
        unique_key='material_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

select * from {{ ref('stg_material') }}

{% endsnapshot %}
