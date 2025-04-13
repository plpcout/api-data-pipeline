{{
    config(
        schema='raw',
        materialized='table',
        alias='raw_earthquakes',
    )
}}

with source as (
        select * from {{ source('raw_eq_dataset', 'raw_eq_data_20*') }}
  )

select * from source
