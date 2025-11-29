{{ config(materialized='view') }}

with raw as (
  select * from {{ source('landing', 'orders') }}
),

-- compute a proper timestamp field, capture the original row as JSON, and rank duplicates
typed_and_ranked as (
  select
    raw.*,                                -- keep all original columns
    to_json_string(raw) as raw_row,       -- <--- store raw payload here

    -- Try to cast order_ts to TIMESTAMP. SAFE_CAST returns NULL for malformed values.
    case
      when order_ts is not null then SAFE_CAST(order_ts AS TIMESTAMP)
      when created_at is not null then SAFE_CAST(created_at AS TIMESTAMP)
      else null
    end as _order_ts_parsed,

    -- dedupe: keep the most recent row per order_id
    row_number() over (
      partition by order_id
      order by
        case
          when order_ts is not null then SAFE_CAST(order_ts AS TIMESTAMP)
          when created_at is not null then SAFE_CAST(created_at AS TIMESTAMP)
          else TIMESTAMP('1970-01-01')
        end desc
    ) as rn
  from raw
),

typed as (
  select
    cast(order_id as string)        as order_id,
    cast(customer_id as string)     as customer_id,

    -- product/order item fields
    cast(product_id as string)      as product_id,
    safe_cast(quantity as int64)    as quantity,

    -- numeric fields
    cast(unit_price as numeric)     as unit_price,
    cast(order_total as numeric)    as order_total,

    order_status,

    -- canonical timestamp
    _order_ts_parsed                as order_created_at,

    -- dev/debug column that stores the raw row as JSON
    raw_row                         as _raw_payload
  from typed_and_ranked
  where rn = 1
)

select * from typed