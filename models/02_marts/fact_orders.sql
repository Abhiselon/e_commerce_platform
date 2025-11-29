{{ config(materialized='table') }}

{% if var('use_order_items', default=False) %}
with items as (
  select
    order_id,
    sum(quantity) as items_count,
    sum(quantity * price_each) as order_total_calc,
    min(order_created_at) as order_created_at
  from {{ ref('fact_order_items') }}
  group by 1
)
select
  i.order_id,
  i.items_count,
  i.order_total_calc as order_total,
  i.order_created_at,
  o.order_status,
  o.customer_id
from items i
left join {{ ref('stg_orders') }} o on i.order_id = o.order_id

{% else %}

select
  order_id,
  1 as items_count,
  order_total,
  order_created_at,
  order_status,
  customer_id
from {{ ref('stg_orders') }}

{% endif %}
