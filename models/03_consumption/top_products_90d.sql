{{ config(materialized='table') }}

select
  p.product_id,
  p.product_name,
  sum(oi.quantity * oi.unit_price) as revenue_90d,
  sum(oi.quantity) as quantity_sold
from {{ ref('fact_order_items') }} oi
join {{ ref('dim_products') }} p on oi.product_id = p.product_id
where oi.order_created_at >= timestamp_sub(current_timestamp(), interval 90 day)
group by 1,2
order by revenue_90d desc
limit 50
