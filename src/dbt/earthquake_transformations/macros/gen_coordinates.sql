{% macro gen_coordinates(longitude, latitude) %}
    case
        when {{ latitude }} is not null and {{ longitude }} is not null then
        concat(
            'POINT(',
            {{ dbt.safe_cast(longitude, api.Column.translate_type('string')) }},
            ' ',
            {{ dbt.safe_cast(latitude, api.Column.translate_type('string')) }},
            ')'
        )
        else null
    end
{% endmacro %}
