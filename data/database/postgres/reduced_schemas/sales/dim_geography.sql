SELECT
    geography_key,
    city,
    state_province_code,
    state_province_name,
    country_region_code,
    english_country_region_name,
    spanish_country_region_name,
    -- french_country_region_name,
    postal_code,
    sales_territory_key
    -- ip_address_locator

FROM
    adventure_works.dim_geography