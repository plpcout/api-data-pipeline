{{
    config(
        schema='mart',
        materialized='table',
        alias='daily_earthquake_summary',
        persist_docs={"relation": true, "columns": true},
    )
}}

select
    event_date,
    count(*) as total_earthquakes,
    round(avg(magnitude), 1) as avg_magnitude,
    max(magnitude) as max_magnitude,
    min(magnitude) as min_magnitude,
    sum(case when magnitude >= 5.0 then 1 else 0 end) as major_earthquakes_count,
    sum(case when tsunami_alert = 1 then 1 else 0 end) as tsunami_alerts_count,
    round(avg(depth_km), 1) as avg_depth_km,
    sum(felt) as total_felt_reports,
    sum(population_nearby) as total_population_affected,
    array_agg(distinct magnitude_category order by magnitude_category) as magnitude_categories,
    array_agg(distinct depth_category order by depth_category) as depth_categories
from {{ ref('fact_earthquakes') }}
group by 1
order by event_date desc
