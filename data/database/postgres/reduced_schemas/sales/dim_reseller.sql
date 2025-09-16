WITH
    years_dif AS (
        SELECT
            (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM MAX(order_date))) + 1 AS years_difference

        FROM (
            SELECT order_date FROM adventure_works.fact_internet_sales
            UNION
            SELECT order_date FROM adventure_works.fact_reseller_sales
        )
    )


SELECT
    reseller_key,
    geography_key,
    -- reseller_alternate_key,
    -- phone,
    business_type,
    reseller_name,
    number_employees,
    order_frequency,
    -- order_month,
    first_order_year,
    last_order_year,
    product_line,
    -- address_line1,
    -- address_line2,
    -- annual_sales,
    -- bank_name,
    -- min_payment_type,
    -- min_payment_amount,
    -- annual_revenue,
    (year_opened + (SELECT years_difference FROM years_dif)) AS year_opened

FROM
    adventure_works.dim_reseller