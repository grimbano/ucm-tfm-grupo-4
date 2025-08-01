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
        (order_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS order_date,
        (due_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS due_date,
        (ship_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS ship_date,
        'internet_sales' AS sale_source

    FROM 
        adventure_works.fact_internet_sales
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
        (order_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS order_date,
        (due_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS due_date,
        (ship_date + ((SELECT years_difference FROM years_dif)::TEXT || ' years')::INTERVAL)::DATE AS ship_date,
        'reseller_sales' AS sale_source

    FROM 
        adventure_works.fact_reseller_sales
)
