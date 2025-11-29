{{ config(materialized='table') }}

select
  DATE(order_created_at) as order_date,
  count(distinct order_id) as orders,
  sum(order_total) as revenue,
  round(sum(order_total) / nullif(count(distinct order_id),0),2) as aov
from {{ ref('fact_orders') }}
group by 1
order by 1
