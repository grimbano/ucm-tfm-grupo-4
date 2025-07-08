DROP DATABASE IF EXISTS adventure_works_dw;
CREATE DATABASE adventure_works_dw;
\c adventure_works_dw;

DROP SCHEMA IF EXISTS public;
CREATE SCHEMA adventure_works;

CREATE TABLE adventure_works.dim_account (
    account_key SERIAL NOT NULL,
    parent_account_key INT,
    account_code_alternate_key INT,
    parent_account_code_alternate_key INT,
    account_description VARCHAR(50),
    account_type VARCHAR(50),
    operator VARCHAR(50),
    custom_members VARCHAR(300),
    value_type VARCHAR(50),
    custom_member_options VARCHAR(200)
);

CREATE TABLE adventure_works.dim_currency (
    currency_key SERIAL NOT NULL,
    currency_alternate_key CHAR(3) NOT NULL,
    currency_name VARCHAR(50) NOT NULL
);

CREATE TABLE adventure_works.dim_customer (
    customer_key SERIAL NOT NULL,
    geography_key INT,
    customer_alternate_key VARCHAR(15) NOT NULL,
    title VARCHAR(8),
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    last_name VARCHAR(50),
    name_style BOOLEAN,
    birth_date DATE,
    marital_status CHAR(1),
    suffix VARCHAR(10),
    gender VARCHAR(1),
    email_address VARCHAR(50),
    yearly_income NUMERIC(19,4),
    total_children SMALLINT,
    number_children_at_home SMALLINT,
    english_education VARCHAR(40),
    spanish_education VARCHAR(40),
    french_education VARCHAR(40),
    english_occupation VARCHAR(100),
    spanish_occupation VARCHAR(100),
    french_occupation VARCHAR(100),
    house_owner_flag CHAR(1),
    number_cars_owned SMALLINT,
    address_line1 VARCHAR(120),
    address_line2 VARCHAR(120),
    phone VARCHAR(20),
    date_first_purchase DATE,
    commute_distance VARCHAR(15)
);

CREATE TABLE adventure_works.dim_date (
    date_key INT NOT NULL,
    full_date_alternate_key DATE NOT NULL,
    day_number_of_week SMALLINT NOT NULL,
    english_day_name_of_week VARCHAR(10) NOT NULL,
    spanish_day_name_of_week VARCHAR(10) NOT NULL,
    french_day_name_of_week VARCHAR(10) NOT NULL,
    day_number_of_month SMALLINT NOT NULL,
    day_number_of_year SMALLINT NOT NULL,
    week_number_of_year SMALLINT NOT NULL,
    english_month_name VARCHAR(10) NOT NULL,
    spanish_month_name VARCHAR(10) NOT NULL,
    french_month_name VARCHAR(10) NOT NULL,
    month_number_of_year SMALLINT NOT NULL,
    calendar_quarter SMALLINT NOT NULL,
    calendar_year SMALLINT NOT NULL,
    calendar_semester SMALLINT NOT NULL,
    fiscal_quarter SMALLINT NOT NULL,
    fiscal_year SMALLINT NOT NULL,
    fiscal_semester SMALLINT NOT NULL
);

CREATE TABLE adventure_works.dim_department_group (
    department_group_key SERIAL NOT NULL,
    parent_department_group_key INT,
    department_group_name VARCHAR(50)
);

CREATE TABLE adventure_works.dim_employee (
    employee_key SERIAL NOT NULL,
    parent_employee_key INT,
    employee_national_id_alternate_key VARCHAR(15),
    parent_employee_national_id_alternate_key VARCHAR(15),
    sales_territory_key INT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    name_style BOOLEAN NOT NULL,
    title VARCHAR(50),
    hire_date DATE,
    birth_date DATE,
    login_id VARCHAR(256),
    email_address VARCHAR(50),
    phone VARCHAR(25),
    marital_status CHAR(1),
    emergency_contact_name VARCHAR(50),
    emergency_contact_phone VARCHAR(25),
    salaried_flag BOOLEAN,
    gender CHAR(1),
    pay_frequency SMALLINT,
    base_rate NUMERIC(19,4),
    vacation_hours SMALLINT,
    sick_leave_hours SMALLINT,
    current_flag BOOLEAN NOT NULL,
    sales_person_flag BOOLEAN NOT NULL,
    department_name VARCHAR(50),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    employee_photo BYTEA
);

CREATE TABLE adventure_works.dim_geography (
    geography_key SERIAL NOT NULL,
    city VARCHAR(30),
    state_province_code VARCHAR(3),
    state_province_name VARCHAR(50),
    country_region_code VARCHAR(3),
    english_country_region_name VARCHAR(50),
    spanish_country_region_name VARCHAR(50),
    french_country_region_name VARCHAR(50),
    postal_code VARCHAR(15),
    sales_territory_key INT,
    ip_address_locator VARCHAR(15)
);

CREATE TABLE adventure_works.dim_organization (
    organization_key SERIAL NOT NULL,
    parent_organization_key INT,
    percentage_of_ownership VARCHAR(16),
    organization_name VARCHAR(50),
    currency_key INT
);

CREATE TABLE adventure_works.dim_product (
    product_key SERIAL NOT NULL,
    product_alternate_key VARCHAR(25),
    product_subcategory_key INT,
    weight_unit_measure_code CHAR(3),
    size_unit_measure_code CHAR(3),
    english_product_name VARCHAR(50),
    spanish_product_name VARCHAR(50),
    french_product_name VARCHAR(50),
    standard_cost NUMERIC(19,4),
    finished_goods_flag BOOLEAN NOT NULL,
    color VARCHAR(15) NOT NULL,
    safety_stock_level SMALLINT,
    reorder_point SMALLINT,
    list_price NUMERIC(19,4),
    size VARCHAR(50),
    size_range VARCHAR(50),
    weight FLOAT,
    days_to_manufacture INT,
    product_line CHAR(2),
    dealer_price NUMERIC(19,4),
    class CHAR(2),
    style CHAR(2),
    model_name VARCHAR(50),
    large_photo BYTEA,
    english_description VARCHAR(400),
    french_description VARCHAR(400),
    chinese_description VARCHAR(400),
    arabic_description VARCHAR(400),
    hebrew_description VARCHAR(400),
    thai_description VARCHAR(400),
    german_description VARCHAR(400),
    japanese_description VARCHAR(400),
    turkish_description VARCHAR(400),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status VARCHAR(7)
);

CREATE TABLE adventure_works.dim_product_category (
    product_category_key SERIAL NOT NULL,
    product_category_alternate_key INT,
    english_product_category_name VARCHAR(50) NOT NULL,
    spanish_product_category_name VARCHAR(50) NOT NULL,
    french_product_category_name VARCHAR(50) NOT NULL
);

CREATE TABLE adventure_works.dim_product_subcategory (
    product_subcategory_key SERIAL NOT NULL,
    product_subcategory_alternate_key INT,
    english_product_subcategory_name VARCHAR(50) NOT NULL,
    spanish_product_subcategory_name VARCHAR(50) NOT NULL,
    french_product_subcategory_name VARCHAR(50) NOT NULL,
    product_category_key INT
);

CREATE TABLE adventure_works.dim_promotion (
    promotion_key SERIAL NOT NULL,
    promotion_alternate_key INT,
    english_promotion_name VARCHAR(255),
    spanish_promotion_name VARCHAR(255),
    french_promotion_name VARCHAR(255),
    discount_pct FLOAT,
    english_promotion_type VARCHAR(50),
    spanish_promotion_type VARCHAR(50),
    french_promotion_type VARCHAR(50),
    english_promotion_category VARCHAR(50),
    spanish_promotion_category VARCHAR(50),
    french_promotion_category VARCHAR(50),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    min_qty INT,
    max_qty INT
);

CREATE TABLE adventure_works.dim_reseller (
    reseller_key SERIAL NOT NULL,
    geography_key INT,
    reseller_alternate_key VARCHAR(15),
    phone VARCHAR(25),
    business_type VARCHAR(20) NOT NULL,
    reseller_name VARCHAR(50) NOT NULL,
    number_employees INT,
    order_frequency CHAR(1),
    order_month SMALLINT,
    first_order_year INT,
    last_order_year INT,
    product_line VARCHAR(50),
    address_line1 VARCHAR(60),
    address_line2 VARCHAR(60),
    annual_sales NUMERIC(19,4),
    bank_name VARCHAR(50),
    min_payment_type SMALLINT,
    min_payment_amount NUMERIC(19,4),
    annual_revenue NUMERIC(19,4),
    year_opened INT
);

CREATE TABLE adventure_works.dim_sales_reason (
    sales_reason_key SERIAL NOT NULL,
    sales_reason_alternate_key INT NOT NULL,
    sales_reason_name VARCHAR(50) NOT NULL,
    sales_reason_reason_type VARCHAR(50) NOT NULL
);

CREATE TABLE adventure_works.dim_sales_territory (
    sales_territory_key SERIAL NOT NULL,
    sales_territory_alternate_key INT,
    sales_territory_region VARCHAR(50) NOT NULL,
    sales_territory_country VARCHAR(50) NOT NULL,
    sales_territory_group VARCHAR(50),
    sales_territory_image BYTEA
);

CREATE TABLE adventure_works.dim_scenario (
    scenario_key SERIAL NOT NULL,
    scenario_name VARCHAR(50)
);

CREATE TABLE adventure_works.fact_additional_international_product_description (
    product_key INT NOT NULL,
    culture_name VARCHAR(50) NOT NULL,
    product_description TEXT NOT NULL
);

CREATE TABLE adventure_works.fact_call_center (
    fact_call_center_id SERIAL NOT NULL,
    date_key INT NOT NULL,
    wage_type VARCHAR(15) NOT NULL,
    shift VARCHAR(20) NOT NULL,
    level_one_operators SMALLINT NOT NULL,
    level_two_operators SMALLINT NOT NULL,
    total_operators SMALLINT NOT NULL,
    calls INT NOT NULL,
    automatic_responses INT NOT NULL,
    orders INT NOT NULL,
    issues_raised SMALLINT NOT NULL,
    average_time_per_issue SMALLINT NOT NULL,
    service_grade FLOAT NOT NULL,
    date TIMESTAMP
);

CREATE TABLE adventure_works.fact_currency_rate (
    currency_key INT NOT NULL,
    date_key INT NOT NULL,
    average_rate FLOAT NOT NULL,
    end_of_day_rate FLOAT NOT NULL,
    date TIMESTAMP
);

CREATE TABLE adventure_works.fact_finance (
    finance_key SERIAL NOT NULL,
    date_key INT NOT NULL,
    organization_key INT NOT NULL,
    department_group_key INT NOT NULL,
    scenario_key INT NOT NULL,
    account_key INT NOT NULL,
    amount FLOAT NOT NULL,
    date TIMESTAMP
);

CREATE TABLE adventure_works.fact_internet_sales (
    product_key INT NOT NULL,
    order_date_key INT NOT NULL,
    due_date_key INT NOT NULL,
    ship_date_key INT NOT NULL,
    customer_key INT NOT NULL,
    promotion_key INT NOT NULL,
    currency_key INT NOT NULL,
    sales_territory_key INT NOT NULL,
    sales_order_number VARCHAR(20) NOT NULL,
    sales_order_line_number SMALLINT NOT NULL,
    revision_number SMALLINT NOT NULL,
    order_quantity SMALLINT NOT NULL,
    unit_price NUMERIC(19,4) NOT NULL,
    extended_amount NUMERIC(19,4) NOT NULL,
    unit_price_discount_pct FLOAT NOT NULL,
    discount_amount FLOAT NOT NULL,
    product_standard_cost NUMERIC(19,4) NOT NULL,
    total_product_cost NUMERIC(19,4) NOT NULL,
    sales_amount NUMERIC(19,4) NOT NULL,
    tax_amt NUMERIC(19,4) NOT NULL,
    freight NUMERIC(19,4) NOT NULL,
    carrier_tracking_number VARCHAR(25),
    customer_po_number VARCHAR(25),
    order_date TIMESTAMP,
    due_date TIMESTAMP,
    ship_date TIMESTAMP
);

CREATE TABLE adventure_works.fact_internet_sales_reason (
    sales_order_number VARCHAR(20) NOT NULL,
    sales_order_line_number SMALLINT NOT NULL,
    sales_reason_key INT NOT NULL
);

CREATE TABLE adventure_works.fact_product_inventory (
    product_key INT NOT NULL,
    date_key INT NOT NULL,
    movement_date DATE NOT NULL,
    unit_cost NUMERIC(19,4) NOT NULL,
    units_in INT NOT NULL,
    units_out INT NOT NULL,
    units_balance INT NOT NULL
);

CREATE TABLE adventure_works.fact_reseller_sales (
    product_key INT NOT NULL,
    order_date_key INT NOT NULL,
    due_date_key INT NOT NULL,
    ship_date_key INT NOT NULL,
    reseller_key INT NOT NULL,
    employee_key INT NOT NULL,
    promotion_key INT NOT NULL,
    currency_key INT NOT NULL,
    sales_territory_key INT NOT NULL,
    sales_order_number VARCHAR(20) NOT NULL,
    sales_order_line_number SMALLINT NOT NULL,
    revision_number SMALLINT,
    order_quantity SMALLINT,
    unit_price NUMERIC(19,4),
    extended_amount NUMERIC(19,4),
    unit_price_discount_pct FLOAT,
    discount_amount FLOAT,
    product_standard_cost NUMERIC(19,4),
    total_product_cost NUMERIC(19,4),
    sales_amount NUMERIC(19,4),
    tax_amt NUMERIC(19,4),
    freight NUMERIC(19,4),
    carrier_tracking_number VARCHAR(25),
    customer_po_number VARCHAR(25),
    order_date TIMESTAMP,
    due_date TIMESTAMP,
    ship_date TIMESTAMP
);

CREATE TABLE adventure_works.fact_sales_quota (
    sales_quota_key SERIAL NOT NULL,
    employee_key INT NOT NULL,
    date_key INT NOT NULL,
    calendar_year SMALLINT NOT NULL,
    calendar_quarter SMALLINT NOT NULL,
    sales_amount_quota NUMERIC(19,4) NOT NULL,
    date TIMESTAMP
);

CREATE TABLE adventure_works.fact_survey_response (
    survey_response_key SERIAL NOT NULL,
    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_category_key INT NOT NULL,
    english_product_category_name VARCHAR(50) NOT NULL,
    product_subcategory_key INT NOT NULL,
    english_product_subcategory_name VARCHAR(50) NOT NULL,
    date TIMESTAMP
);

CREATE TABLE adventure_works.new_fact_currency_rate (
    average_rate REAL,
    currency_id VARCHAR(3),
    currency_date DATE,
    end_of_day_rate REAL,
    currency_key INT,
    date_key INT
);

CREATE TABLE adventure_works.prospective_buyer (
    prospective_buyer_key SERIAL NOT NULL,
    prospect_alternate_key VARCHAR(15),
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    last_name VARCHAR(50),
    birth_date TIMESTAMP,
    marital_status CHAR(1),
    gender VARCHAR(1),
    email_address VARCHAR(50),
    yearly_income NUMERIC(19,4),
    total_children SMALLINT,
    number_children_at_home SMALLINT,
    education VARCHAR(40),
    occupation VARCHAR(100),
    house_owner_flag CHAR(1),
    number_cars_owned SMALLINT,
    address_line1 VARCHAR(120),
    address_line2 VARCHAR(120),
    city VARCHAR(30),
    state_province_code VARCHAR(3),
    postal_code VARCHAR(15),
    phone VARCHAR(20),
    salutation VARCHAR(8),
    unknown INT
);

COPY adventure_works.dim_account FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimAccount.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_currency FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimCurrency.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_customer FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimCustomer.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_date FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimDate.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_department_group FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimDepartmentGroup.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_employee FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimEmployee.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_geography FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimGeography.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_organization FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimOrganization.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_product FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimProduct.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_product_category FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimProductCategory.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_product_subcategory FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimProductSubcategory.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_promotion FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimPromotion.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_reseller FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimReseller.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_sales_reason FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimSalesReason.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_sales_territory FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimSalesTerritory.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.dim_scenario FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/DimScenario.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_additional_international_product_description FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactAdditionalInternationalProductDescription.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_call_center FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactCallCenter.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_currency_rate FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactCurrencyRate.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_finance FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactFinance.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_internet_sales FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactInternetSales.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_internet_sales_reason FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactInternetSalesReason.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_product_inventory FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactProductInventory.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_reseller_sales FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactResellerSales.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_sales_quota FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactSalesQuota.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.fact_survey_response FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/FactSurveyResponse.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.new_fact_currency_rate FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/NewFactCurrencyRate.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');
COPY adventure_works.prospective_buyer FROM 'C:/python/ucm-tfm-grupo-4/data/database/postgres/ProspectiveBuyer.csv' WITH (DELIMITER '|', FORMAT CSV, HEADER FALSE, ENCODING 'UTF8');

ALTER TABLE adventure_works.dim_account ADD PRIMARY KEY (account_key);
ALTER TABLE adventure_works.dim_currency ADD PRIMARY KEY (currency_key);
ALTER TABLE adventure_works.dim_customer ADD PRIMARY KEY (customer_key);
ALTER TABLE adventure_works.dim_date ADD PRIMARY KEY (date_key);
ALTER TABLE adventure_works.dim_department_group ADD PRIMARY KEY (department_group_key);
ALTER TABLE adventure_works.dim_employee ADD PRIMARY KEY (employee_key);
ALTER TABLE adventure_works.dim_geography ADD PRIMARY KEY (geography_key);
ALTER TABLE adventure_works.dim_organization ADD PRIMARY KEY (organization_key);
ALTER TABLE adventure_works.dim_product ADD PRIMARY KEY (product_key);
ALTER TABLE adventure_works.dim_product_category ADD PRIMARY KEY (product_category_key);
ALTER TABLE adventure_works.dim_product_subcategory ADD PRIMARY KEY (product_subcategory_key);
ALTER TABLE adventure_works.dim_promotion ADD PRIMARY KEY (promotion_key);
ALTER TABLE adventure_works.dim_reseller ADD PRIMARY KEY (reseller_key);
ALTER TABLE adventure_works.dim_sales_reason ADD PRIMARY KEY (sales_reason_key);
ALTER TABLE adventure_works.dim_sales_territory ADD PRIMARY KEY (sales_territory_key);
ALTER TABLE adventure_works.dim_scenario ADD PRIMARY KEY (scenario_key);
ALTER TABLE adventure_works.fact_additional_international_product_description ADD PRIMARY KEY (product_key, culture_name);
ALTER TABLE adventure_works.fact_call_center ADD PRIMARY KEY (fact_call_center_id);
ALTER TABLE adventure_works.fact_currency_rate ADD PRIMARY KEY (currency_key, date_key);
ALTER TABLE adventure_works.fact_finance ADD PRIMARY KEY (finance_key);
ALTER TABLE adventure_works.fact_internet_sales ADD PRIMARY KEY (sales_order_number, sales_order_line_number);
ALTER TABLE adventure_works.fact_internet_sales_reason ADD PRIMARY KEY (sales_order_number, sales_order_line_number, sales_reason_key);
ALTER TABLE adventure_works.fact_product_inventory ADD PRIMARY KEY (product_key, date_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD PRIMARY KEY (sales_order_number, sales_order_line_number);
ALTER TABLE adventure_works.fact_sales_quota ADD PRIMARY KEY (sales_quota_key);
ALTER TABLE adventure_works.fact_survey_response ADD PRIMARY KEY (survey_response_key);
ALTER TABLE adventure_works.prospective_buyer ADD PRIMARY KEY (prospective_buyer_key);

CREATE UNIQUE INDEX idx_dim_currency_currency_alternate_key ON adventure_works.dim_currency (currency_alternate_key);
CREATE UNIQUE INDEX idx_dim_customer_customer_alternate_key ON adventure_works.dim_customer (customer_alternate_key);
CREATE UNIQUE INDEX idx_dim_date_full_date_alternate_key ON adventure_works.dim_date (full_date_alternate_key);
CREATE UNIQUE INDEX idx_dim_product_product_alternate_key_start_date ON adventure_works.dim_product (product_alternate_key, start_date);
CREATE UNIQUE INDEX idx_dim_product_category_product_category_alternate_key ON adventure_works.dim_product_category (product_category_alternate_key);
CREATE UNIQUE INDEX idx_dim_product_subcategory_product_subcategory_alternate_key ON adventure_works.dim_product_subcategory (product_subcategory_alternate_key);
CREATE UNIQUE INDEX idx_dim_promotion_promotion_alternate_key ON adventure_works.dim_promotion (promotion_alternate_key);
CREATE UNIQUE INDEX idx_dim_reseller_reseller_alternate_key ON adventure_works.dim_reseller (reseller_alternate_key);
CREATE UNIQUE INDEX idx_dim_sales_territory_sales_territory_alternate_key ON adventure_works.dim_sales_territory (sales_territory_alternate_key);
CREATE UNIQUE INDEX idx_fact_call_center_date_key_shift ON adventure_works.fact_call_center (date_key, shift);

ALTER TABLE adventure_works.dim_account ADD CONSTRAINT fk_dim_account_parent_account FOREIGN KEY (parent_account_key) REFERENCES adventure_works.dim_account (account_key);
ALTER TABLE adventure_works.dim_customer ADD CONSTRAINT fk_dim_customer_geography FOREIGN KEY (geography_key) REFERENCES adventure_works.dim_geography (geography_key);
ALTER TABLE adventure_works.dim_department_group ADD CONSTRAINT fk_dim_department_group_parent_department_group FOREIGN KEY (parent_department_group_key) REFERENCES adventure_works.dim_department_group (department_group_key);
ALTER TABLE adventure_works.dim_employee ADD CONSTRAINT fk_dim_employee_sales_territory FOREIGN KEY (sales_territory_key) REFERENCES adventure_works.dim_sales_territory (sales_territory_key);
ALTER TABLE adventure_works.dim_employee ADD CONSTRAINT fk_dim_employee_parent_employee FOREIGN KEY (parent_employee_key) REFERENCES adventure_works.dim_employee (employee_key);
ALTER TABLE adventure_works.dim_geography ADD CONSTRAINT fk_dim_geography_sales_territory FOREIGN KEY (sales_territory_key) REFERENCES adventure_works.dim_sales_territory (sales_territory_key);
ALTER TABLE adventure_works.dim_organization ADD CONSTRAINT fk_dim_organization_currency FOREIGN KEY (currency_key) REFERENCES adventure_works.dim_currency (currency_key);
ALTER TABLE adventure_works.dim_organization ADD CONSTRAINT fk_dim_organization_parent_organization FOREIGN KEY (parent_organization_key) REFERENCES adventure_works.dim_organization (organization_key);
ALTER TABLE adventure_works.dim_product ADD CONSTRAINT fk_dim_product_product_subcategory FOREIGN KEY (product_subcategory_key) REFERENCES adventure_works.dim_product_subcategory (product_subcategory_key);
ALTER TABLE adventure_works.dim_product_subcategory ADD CONSTRAINT fk_dim_product_subcategory_product_category FOREIGN KEY (product_category_key) REFERENCES adventure_works.dim_product_category (product_category_key);
ALTER TABLE adventure_works.dim_reseller ADD CONSTRAINT fk_dim_reseller_geography FOREIGN KEY (geography_key) REFERENCES adventure_works.dim_geography (geography_key);
ALTER TABLE adventure_works.fact_call_center ADD CONSTRAINT fk_fact_call_center_date FOREIGN KEY (date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_currency_rate ADD CONSTRAINT fk_fact_currency_rate_date FOREIGN KEY (date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_currency_rate ADD CONSTRAINT fk_fact_currency_rate_currency FOREIGN KEY (currency_key) REFERENCES adventure_works.dim_currency (currency_key);
ALTER TABLE adventure_works.fact_finance ADD CONSTRAINT fk_fact_finance_scenario FOREIGN KEY (scenario_key) REFERENCES adventure_works.dim_scenario (scenario_key);
ALTER TABLE adventure_works.fact_finance ADD CONSTRAINT fk_fact_finance_organization FOREIGN KEY (organization_key) REFERENCES adventure_works.dim_organization (organization_key);
ALTER TABLE adventure_works.fact_finance ADD CONSTRAINT fk_fact_finance_department_group FOREIGN KEY (department_group_key) REFERENCES adventure_works.dim_department_group (department_group_key);
ALTER TABLE adventure_works.fact_finance ADD CONSTRAINT fk_fact_finance_date FOREIGN KEY (date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_finance ADD CONSTRAINT fk_fact_finance_account FOREIGN KEY (account_key) REFERENCES adventure_works.dim_account (account_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_currency FOREIGN KEY (currency_key) REFERENCES adventure_works.dim_currency (currency_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_customer FOREIGN KEY (customer_key) REFERENCES adventure_works.dim_customer (customer_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_order_date FOREIGN KEY (order_date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_due_date FOREIGN KEY (due_date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_ship_date FOREIGN KEY (ship_date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_product FOREIGN KEY (product_key) REFERENCES adventure_works.dim_product (product_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_promotion FOREIGN KEY (promotion_key) REFERENCES adventure_works.dim_promotion (promotion_key);
ALTER TABLE adventure_works.fact_internet_sales ADD CONSTRAINT fk_fact_internet_sales_sales_territory FOREIGN KEY (sales_territory_key) REFERENCES adventure_works.dim_sales_territory (sales_territory_key);
ALTER TABLE adventure_works.fact_internet_sales_reason ADD CONSTRAINT fk_fact_internet_sales_reason_fact_internet_sales FOREIGN KEY (sales_order_number, sales_order_line_number) REFERENCES adventure_works.fact_internet_sales (sales_order_number, sales_order_line_number);
ALTER TABLE adventure_works.fact_internet_sales_reason ADD CONSTRAINT fk_fact_internet_sales_reason_sales_reason FOREIGN KEY (sales_reason_key) REFERENCES adventure_works.dim_sales_reason (sales_reason_key);
ALTER TABLE adventure_works.fact_product_inventory ADD CONSTRAINT fk_fact_product_inventory_date FOREIGN KEY (date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_product_inventory ADD CONSTRAINT fk_fact_product_inventory_product FOREIGN KEY (product_key) REFERENCES adventure_works.dim_product (product_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_currency FOREIGN KEY (currency_key) REFERENCES adventure_works.dim_currency (currency_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_order_date FOREIGN KEY (order_date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_due_date FOREIGN KEY (due_date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_ship_date FOREIGN KEY (ship_date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_employee FOREIGN KEY (employee_key) REFERENCES adventure_works.dim_employee (employee_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_product FOREIGN KEY (product_key) REFERENCES adventure_works.dim_product (product_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_promotion FOREIGN KEY (promotion_key) REFERENCES adventure_works.dim_promotion (promotion_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_reseller FOREIGN KEY (reseller_key) REFERENCES adventure_works.dim_reseller (reseller_key);
ALTER TABLE adventure_works.fact_reseller_sales ADD CONSTRAINT fk_fact_reseller_sales_sales_territory FOREIGN KEY (sales_territory_key) REFERENCES adventure_works.dim_sales_territory (sales_territory_key);
ALTER TABLE adventure_works.fact_sales_quota ADD CONSTRAINT fk_fact_sales_quota_employee FOREIGN KEY (employee_key) REFERENCES adventure_works.dim_employee (employee_key);
ALTER TABLE adventure_works.fact_sales_quota ADD CONSTRAINT fk_fact_sales_quota_date FOREIGN KEY (date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_survey_response ADD CONSTRAINT fk_fact_survey_response_date FOREIGN KEY (date_key) REFERENCES adventure_works.dim_date (date_key);
ALTER TABLE adventure_works.fact_survey_response ADD CONSTRAINT fk_fact_survey_response_customer FOREIGN KEY (customer_key) REFERENCES adventure_works.dim_customer (customer_key);