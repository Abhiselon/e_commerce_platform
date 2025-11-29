{{ config(materialized='table') }}

with src as (
  select * from {{ ref('stg_orders') }}
),

with_id as (
  select
    order_id,
    product_id,
    customer_id,
    quantity,
    unit_price,
    order_total,
    order_created_at,
    concat(order_id, '::', product_id) as order_item_id
  from src
)

select * from with_id
