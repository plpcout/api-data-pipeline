{{
    config(
        schema='mart',
        materialized='table',
        alias='geo_earthquake_analysis',
        persist_docs={"relation": true, "columns": true},
    )
}}

select
    country,
    state,
    city,
    count(*) as total_earthquakes,
    round(avg(magnitude), 1) as avg_magnitude,
    max(magnitude) as max_magnitude,
    min(magnitude) as min_magnitude,
    round(avg(depth_km), 1) as avg_depth_km,
    sum(case when magnitude >= 5.0 then 1 else 0 end) as major_earthquakes_count,
    sum(case when tsunami_alert = 1 then 1 else 0 end) as tsunami_alerts_count,
    sum(felt) as total_felt_reports,
    sum(population_nearby) as total_population_affected,
    round(avg(longitude), 1) as center_longitude,
    round(avg(latitude), 1) as center_latitude,
    array_agg(coordinates limit 1)[offset(0)] as sample_coordinates,
    array_agg(distinct magnitude_category order by magnitude_category) as magnitude_categories,
    array_agg(distinct depth_category order by depth_category) as depth_categories,
    array_agg(distinct event_type order by event_type) as event_types
from {{ ref('fact_earthquakes') }}
where country is not null
group by 1, 2, 3
having total_earthquakes > 1
order by total_earthquakes desc
