{{ config(materialized='table') }}

select
  product_id,
  name as product_name,
  category,
  price,
  created_at as product_created_at
from {{ ref('stg_products') }}
