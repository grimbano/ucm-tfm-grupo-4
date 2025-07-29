WITH
    all_sales AS (
        (
            SELECT
                product_key,
                -- order_date_key,
                -- due_date_key,
                -- ship_date_key,
                NULL AS reseller_key,
                NULL AS employee_key,
                customer_key,
                promotion_key,
                -- currency_key,
                sales_territory_key,
                sales_order_number,
                sales_order_line_number,
                -- revision_number,
                order_quantity,
                unit_price,
                extended_amount,
                unit_price_discount_pct,
                discount_amount,
                product_standard_cost,
                total_product_cost,
                sales_amount,
                tax_amt,
                freight,
                -- carrier_tracking_number,
                -- customer_po_number,
                order_date,
                due_date,
                ship_date,
                'internet_sale' AS sale_source
            FROM adventure_works.fact_internet_sales
        )

        UNION

        (
            SELECT 
                product_key,
                -- order_date_key,
                -- due_date_key,
                -- ship_date_key,
                reseller_key,
                employee_key,
                NULL AS customer_key,
                promotion_key,
                -- currency_key,
                sales_territory_key,
                sales_order_number,
                sales_order_line_number,
                -- revision_number,
                order_quantity,
                unit_price,
                extended_amount,
                unit_price_discount_pct,
                discount_amount,
                product_standard_cost,
                total_product_cost,
                sales_amount,
                tax_amt,
                freight,
                -- carrier_tracking_number,
                -- customer_po_number,
                order_date,
                due_date,
                ship_date,
                'reseller_sales' AS sale_source
            FROM adventure_works.fact_reseller_sales
        )
    ),

    years_dif AS (
        SELECT
            (EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM MAX(order_date))) + 1 AS years_difference

        FROM
            all_sales
    )



SELECT
    -- SALES fields
    f.sale_source,
    f.sales_order_number,
    f.sales_order_line_number,
    f.order_quantity,
    f.unit_price,
    f.extended_amount,
    f.unit_price_discount_pct,
    f.discount_amount,
    f.product_standard_cost,
    f.total_product_cost,
    f.sales_amount,
    f.tax_amt,
    f.freight,
    (f.order_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS order_date,
    (f.due_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS due_date,
    (f.ship_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS ship_date,

    -- PRODUCT fields
    p.spanish_product_name,
    p.english_product_name,
    p_c.spanish_product_category_name,
    p_c.english_product_category_name,
    p_sc.spanish_product_subcategory_name,
    p_sc.english_product_subcategory_name,

    -- CUSTOMER fields
    c.customer_key,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_full_name,
    c.marital_status AS customer_marital_status,
    c.gender AS customer_gender,
    c.total_children AS customer_total_children,
    c.number_children_at_home AS customer_number_children_at_home,

    -- RESELLER fields
    r.reseller_key,
    r.business_type AS reseller_business_type,
    r.reseller_name,
    r.product_line AS reseller_product_line,

    -- EMPLOYEE fields
    e.employee_key,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_full_name,

    -- GEOGRAPHICAL fields
    g.city AS sales_territory_city,
    g.state_province_name AS sales_territory_state_province,
    (
        CASE
            WHEN st.sales_territory_country = st.sales_territory_region THEN st.sales_territory_region
            ELSE CONCAT(st.sales_territory_country, ' - ', st.sales_territory_region)
        END
    ) AS sales_territory_region,
    g.spanish_country_region_name AS sales_territory_country,
    st.sales_territory_group

FROM
    all_sales AS f

    -- join PRODUCT dimensions
    INNER JOIN adventure_works.dim_product AS p USING (product_key)
    INNER JOIN adventure_works.dim_product_subcategory AS p_sc USING (product_subcategory_key)
    INNER JOIN adventure_works.dim_product_category AS p_c USING (product_category_key)

    -- join CUSTOMER dimensions
    LEFT JOIN adventure_works.dim_customer AS c USING (customer_key)

    -- join RESELLER dimensions
    LEFT JOIN adventure_works.dim_reseller AS r USING (reseller_key)

    -- join EMPLOYEE dimensions
    LEFT JOIN adventure_works.dim_employee AS e USING (employee_key)

    -- join GEOGRAPHICAL dimensions
    INNER JOIN adventure_works.dim_sales_territory AS st ON (
        st.sales_territory_key = f.sales_territory_key
    )
    INNER JOIN adventure_works.dim_geography AS g ON (
        g.geography_key = COALESCE(c.geography_key, r.geography_key)
    )
;