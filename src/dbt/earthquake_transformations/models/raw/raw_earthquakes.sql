{{
    config(
        schema='raw',
        materialized='incremental',
        alias='raw_earthquakes',
        unique_key='id',
        incremental_strategy='insert_overwrite',
        partition_by={
            "field": "partition_time",
            "data_type": "timestamp",
            "granularity": "month"
        }
    )
}}

with source as (
    select 
        *,
        {{ dbt.safe_cast('properties__time', api.Column.translate_type('timestamp')) }} as partition_time
    from {{ source('raw_eq_dataset', 'raw_eq_data_20*') }}
    {% if is_incremental() %}
    where {{ dbt.safe_cast('properties__time', api.Column.translate_type('timestamp')) }} > (
        select max(partition_time) from {{ this }}
    )
    {% endif %}
)

select * from source
