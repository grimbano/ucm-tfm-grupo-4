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
    employee_key,
    -- parent_employee_key,
    -- employee_national_id_alternate_key,
    -- parent_employee_national_id_alternate_key,
    -- sales_territory_key,
    -- first_name,
    -- last_name,
    -- middle_name,
    -- name_style,
    CONCAT(first_name, ' ', last_name) AS employee_full_name,
    title,
    -- hire_date,
    -- birth_date,
    -- login_id,
    -- email_address,
    -- phone,
    -- marital_status,
    -- emergency_contact_name,
    -- emergency_contact_phone,
    -- salaried_flag,
    gender,
    -- pay_frequency,
    -- base_rate,
    -- vacation_hours,
    -- sick_leave_hours,
    -- current_flag,
    sales_person_flag
    -- department_name,
    -- start_date,
    -- end_date,
    -- status,
    -- employee_photo

FROM
    adventure_works.dim_employee

WHERE
    sales_person_flag