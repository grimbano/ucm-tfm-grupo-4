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
    p.product_key,
    -- p.product_alternate_key,
    -- p.product_subcategory_key,
    p.weight_unit_measure_code,
    p.size_unit_measure_code,
    p.english_product_name,
    p.spanish_product_name,
    -- p.french_product_name,
    p.standard_cost,
    p.finished_goods_flag,
    p.color,
    p.safety_stock_level,
    p.reorder_point,
    p.list_price,
    p.size,
    p.size_range,
    p.weight,
    p.days_to_manufacture,
    p.product_line,
    p.dealer_price,
    p.class,
    p.style,
    p.model_name,
    -- p.large_photo,
    p.english_description,
    -- p.french_description,
    -- p.chinese_description,
    -- p.arabic_description,
    -- p.hebrew_description,
    -- p.thai_description,
    -- p.german_description,
    -- p.japanese_description,
    -- p.turkish_description,
    (p.start_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS start_date,
    (p.end_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS end_date,
    (
        CASE 
            WHEN p.status IS NULL THEN False
            ELSE True
        END
    ) AS active,

    -- p_sc.product_subcategory_key,
    -- p_sc.product_subcategory_alternate_key,
    p_sc.english_product_subcategory_name,
    p_sc.spanish_product_subcategory_name,
    -- p_sc.french_product_subcategory_name,
    -- p_sc.product_category_key,
    
    -- p_c.product_category_key,
    -- p_c.product_category_alternate_key,
    p_c.english_product_category_name,
    p_c.spanish_product_category_name
    -- p_c.french_product_category_name

FROM
    adventure_works.dim_product AS p
    LEFT JOIN adventure_works.dim_product_subcategory AS p_sc USING (product_subcategory_key)
    LEFT JOIN adventure_works.dim_product_category AS p_c USING (product_category_key)

WHERE
    EXISTS (
        SELECT
            1
        FROM (
                SELECT product_key FROM adventure_works.fact_internet_sales
                UNION
                SELECT product_key FROM adventure_works.fact_reseller_sales
            ) AS fact
        WHERE
            fact.product_key = p.product_key
    )
