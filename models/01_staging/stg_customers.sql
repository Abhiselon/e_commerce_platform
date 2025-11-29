{{ config(materialized='view') }}

with raw as (
  select * from {{ source('landing', 'customers') }}
),

normalized as (
  select
    -- assume primary key column is customer_id (if not, change)
    cast(customer_id as string) as customer_id,
    nullif(trim(coalesce(first_name,'') || ' ' || coalesce(last_name,'')), '') as full_name,
    lower(nullif(trim(email), '')) as email,
    case
      when created_at is null then current_timestamp()
      else cast(created_at as timestamp)
    end as created_at,
    -- keep a copy of the raw payload if needed
    to_json_string(raw) as _raw_payload
  from raw
)

select * from normalized
