{{ config(materialized='view') }}

with raw as (
  select * from {{ source('landing', 'products') }}
),

typed as (
  select
    cast(product_id as string) as product_id,
    product_name as name,
    category,
    cast(price as numeric) as price,
    case when created_at is null then current_timestamp() else cast(created_at as timestamp) end as created_at,
    to_json_string(raw) as _raw_payload
  from raw
)

select * from typed
