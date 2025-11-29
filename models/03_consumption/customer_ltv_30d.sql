{{ config(materialized='table') }}

with first_orders as (
  select
    customer_id,
    min(order_created_at) as first_order_at
  from {{ ref('fact_orders') }}
  group by 1
),

revenue_30d as (
  select
    f.customer_id,
    sum(fo.order_total) as revenue_30d
  from first_orders f
  join {{ ref('fact_orders') }} fo
    on fo.customer_id = f.customer_id
    and fo.order_created_at >= f.first_order_at
    and fo.order_created_at < timestamp_add(f.first_order_at, interval 30 day)
  group by 1
)

select
  f.customer_id,
  f.first_order_at,
  coalesce(r.revenue_30d, 0) as revenue_30d
from first_orders f
left join revenue_30d r on f.customer_id = r.customer_id
