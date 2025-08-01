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
    promotion_key,
    -- promotion_alternate_key,
    english_promotion_name,
    spanish_promotion_name,
    -- french_promotion_name,
    discount_pct,
    english_promotion_type,
    spanish_promotion_type,
    -- french_promotion_type,
    english_promotion_category,
    spanish_promotion_category,
    -- french_promotion_category,
    (
        CASE discount_pct
            WHEN 0 THEN NULL
            ELSE (start_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE
        END
    ) AS start_date,
    (
        CASE discount_pct
            WHEN 0 THEN NULL
            ELSE (end_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE
        END
    ) AS end_date,
    min_qty,
    max_qty

FROM
    adventure_works.dim_promotion