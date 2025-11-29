{{ config(materialized='table') }}

with dates as (
  select
    day as date,
    EXTRACT(YEAR FROM day) as year,
    EXTRACT(MONTH FROM day) as month,
    EXTRACT(DAY FROM day) as day_of_month,
    EXTRACT(DAYOFWEEK FROM day) as day_of_week,
    FORMAT_DATE('%Y-%m', day) as year_month
  from
    UNNEST(GENERATE_DATE_ARRAY(DATE_SUB(CURRENT_DATE(), INTERVAL 3650 DAY), DATE_ADD(CURRENT_DATE(), INTERVAL 365 DAY))) as day
)

select * from dates
