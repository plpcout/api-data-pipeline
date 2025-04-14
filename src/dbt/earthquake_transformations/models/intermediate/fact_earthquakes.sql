{{
    config(
        schema='intermediate',
        materialized='table',
        alias='fact_earthquakes',
        persist_docs={"relation": true, "columns": true},
        partition_by={
            "field": "event_date",
            "data_type": "date",
            "granularity": "day"
        },
        cluster_by = ['magnitude_category', 'country', 'depth_category']
    )
}}

with source_earthquakes as (
    select * from {{ ref('stg_earthquakes') }}
),

fact_earthquakes as (
    select
        earthquake_key,
        earthquake_time,
        date(earthquake_time) as event_date,
        extract(year from earthquake_time) as event_year,
        extract(month from earthquake_time) as event_month,
        extract(day from earthquake_time) as event_day,
        extract(hour from earthquake_time) as event_hour,
        latitude,
        longitude,
        concat(
            latitude,
            ',',
            longitude
        ) as coordinates,
        depth_km,
        magnitude,
        event_type,
        raw_location,
        country,
        state,
        city,
        population_nearby,
        felt,
        tsunami_alert
    from source_earthquakes
)

select
    earthquake_key,
    earthquake_time,
    event_date,
    event_year,
    event_month,
    event_day,
    event_hour,
    latitude,
    longitude,
    coordinates,
    depth_km,
    magnitude,
    event_type,
    raw_location,
    country,
    state,
    city,
    population_nearby,
    felt,
    tsunami_alert,
    -- Additional metrics
    case
        when magnitude < 2.0 then 'Micro'
        when magnitude < 4.0 then 'Minor'
        when magnitude < 5.0 then 'Light'
        when magnitude < 6.0 then 'Moderate'
        when magnitude < 7.0 then 'Strong'
        when magnitude < 8.0 then 'Major'
        else 'Great'
    end as magnitude_category,
    case
        when depth_km < 70 then 'Shallow'
        when depth_km < 300 then 'Intermediate'
        else 'Deep'
    end as depth_category
from fact_earthquakes
