{{ config(materialized='table') }}

select
  customer_id,
  full_name,
  email,
  created_at as customer_created_at
from {{ ref('stg_customers') }}
