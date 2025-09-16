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
    customer_key,
    geography_key,
    -- customer_alternate_key,
    -- title,
    -- first_name,
    -- middle_name,
    -- last_name,
    -- name_style,
    CONCAT(first_name, ' ', last_name) AS customer_full_name,
    (birth_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS birth_date,
    marital_status,
    -- suffix,
    gender,
    -- email_address,
    yearly_income,
    total_children,
    number_children_at_home,
    english_education,
    spanish_education,
    -- french_education,
    english_occupation,
    spanish_occupation,
    -- french_occupation,
    (house_owner_flag = '1') AS house_owner,
    number_cars_owned,
    -- address_line1,
    -- address_line2,
    -- phone,
    -- date_first_purchase,
    commute_distance

FROM
    adventure_works.dim_customer