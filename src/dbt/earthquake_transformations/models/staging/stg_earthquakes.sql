{{
    config(
        schema='staging',
        materialized='table',
        alias='stg_earthquakes',
        persist_docs={"relation": true, "columns": true},
        partition_by={
            "field": "earthquake_time",
            "data_type": "timestamp",
            "granularity": "day"
        }
    )
}}

with source as (
    select
        *,
        row_number() over(partition by
            id,
            properties__time,
            {{ dbt.safe_cast('properties__mag', api.Column.translate_type('string')) }}) as rn
    from {{ ref('raw_earthquakes') }}
),

renamed as (
    select
        {{ dbt.safe_cast('id', api.Column.translate_type('string')) }} as source_earthquake_id,
        {{ dbt.safe_cast('properties__mag', api.Column.translate_type('float')) }} as magnitude,
        {{ dbt.safe_cast('properties__time', api.Column.translate_type('timestamp')) }} as earthquake_time,
        {{ dbt.safe_cast('properties__g_depth', api.Column.translate_type('float')) }} as depth_km,
        {{ dbt.safe_cast('properties__g_latitude', api.Column.translate_type('float')) }} as latitude,
        {{ dbt.safe_cast('properties__g_longitude', api.Column.translate_type('float')) }} as longitude,
        {{ dbt.safe_cast('properties__place', api.Column.translate_type('string')) }} as raw_location,
        {{ dbt.safe_cast('properties__type', api.Column.translate_type('string')) }} as event_type,
        {{ dbt.safe_cast('properties__tsunami', api.Column.translate_type('integer')) }} as tsunami_alert,
        {{ dbt.safe_cast('properties__country_code', api.Column.translate_type('string')) }} as country_code,
        {{ dbt.safe_cast('properties__country', api.Column.translate_type('string')) }} as country,
        {{ dbt.safe_cast('properties__state', api.Column.translate_type('string')) }}  as state,
        {{ dbt.safe_cast('properties__city', api.Column.translate_type('string')) }}  as city,
        {{ dbt.safe_cast('properties__population', api.Column.translate_type('integer')) }} as population_nearby,
        {{ dbt.safe_cast('properties__felt', api.Column.translate_type('integer')) }} as felt
    from source
    where rn = 1
)

select
    {{ dbt_utils.generate_surrogate_key(
        ['source_earthquake_id', 'earthquake_time', 'magnitude']
    ) }} AS earthquake_key,
    source_earthquake_id,
    coalesce(magnitude, 0) as magnitude,
    earthquake_time,
    depth_km,
    latitude,
    longitude,
    {{ gen_coordinates('longitude', 'latitude') }} as coordinates,
    raw_location,
    event_type,
    tsunami_alert,
    country,
    state,
    city,
    population_nearby,
    coalesce(felt, 0) as felt

from renamed

{% if var('is_test_run', default=true) %}
    limit 100
{% endif %}
