{{ config(materialized='table') }}

select
  FORMAT_DATE('%Y-%m', DATE(fo.order_created_at)) as year_month,
  p.category,
  count(distinct fo.order_id) as orders,
  sum(oi.quantity * oi.unit_price) as revenue
from {{ ref('fact_order_items') }} oi
left join {{ ref('dim_products') }} p 
  on oi.product_id = p.product_id
left join {{ ref('fact_orders') }} fo 
  on oi.order_id = fo.order_id
group by 1,2
order by 1 desc, 3 desc
