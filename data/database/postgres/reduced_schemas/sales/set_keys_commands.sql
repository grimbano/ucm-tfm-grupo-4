ALTER TABLE [SCHEMA].dim_customer ADD PRIMARY KEY (customer_key)
ALTER TABLE [SCHEMA].dim_sales_person ADD PRIMARY KEY (employee_key);
ALTER TABLE [SCHEMA].dim_geography ADD PRIMARY KEY (geography_key);
ALTER TABLE [SCHEMA].dim_product ADD PRIMARY KEY (product_key);
ALTER TABLE [SCHEMA].dim_promotion ADD PRIMARY KEY (promotion_key);
ALTER TABLE [SCHEMA].dim_reseller ADD PRIMARY KEY (reseller_key);
ALTER TABLE [SCHEMA].dim_sales_reason ADD PRIMARY KEY (sales_reason_key);
ALTER TABLE [SCHEMA].dim_sales_territory ADD PRIMARY KEY (sales_territory_key);
ALTER TABLE [SCHEMA].fact_sales ADD PRIMARY KEY (sales_order_number, sales_order_line_number);
ALTER TABLE [SCHEMA].fact_internet_sales_reason ADD PRIMARY KEY (sales_order_number, sales_order_line_number, sales_reason_key);

ALTER TABLE [SCHEMA].dim_customer ADD CONSTRAINT fk_dim_customer_geography FOREIGN KEY (geography_key) REFERENCES [SCHEMA].dim_geography (geography_key);
ALTER TABLE [SCHEMA].dim_geography ADD CONSTRAINT fk_dim_geography_sales_territory FOREIGN KEY (sales_territory_key) REFERENCES [SCHEMA].dim_sales_territory (sales_territory_key);
ALTER TABLE [SCHEMA].dim_reseller ADD CONSTRAINT fk_dim_reseller_geography FOREIGN KEY (geography_key) REFERENCES [SCHEMA].dim_geography (geography_key);
ALTER TABLE [SCHEMA].fact_sales ADD CONSTRAINT fk_fact_sales_person FOREIGN KEY (employee_key) REFERENCES [SCHEMA].dim_sales_person (employee_key);
ALTER TABLE [SCHEMA].fact_sales ADD CONSTRAINT fk_fact_sales_reseller FOREIGN KEY (reseller_key) REFERENCES [SCHEMA].dim_reseller (reseller_key);
ALTER TABLE [SCHEMA].fact_sales ADD CONSTRAINT fk_fact_sales_customer FOREIGN KEY (customer_key) REFERENCES [SCHEMA].dim_customer (customer_key);
ALTER TABLE [SCHEMA].fact_sales ADD CONSTRAINT fk_fact_sales_product FOREIGN KEY (product_key) REFERENCES [SCHEMA].dim_product (product_key);
ALTER TABLE [SCHEMA].fact_sales ADD CONSTRAINT fk_fact_sales_promotion FOREIGN KEY (promotion_key) REFERENCES [SCHEMA].dim_promotion (promotion_key);
ALTER TABLE [SCHEMA].fact_sales ADD CONSTRAINT fk_fact_sales_sales_territory FOREIGN KEY (sales_territory_key) REFERENCES [SCHEMA].dim_sales_territory (sales_territory_key);
ALTER TABLE [SCHEMA].fact_internet_sales_reason ADD CONSTRAINT fk_fact_internet_sales_reason_fact_sales FOREIGN KEY (sales_order_number, sales_order_line_number) REFERENCES [SCHEMA].fact_sales (sales_order_number, sales_order_line_number);
ALTER TABLE [SCHEMA].fact_internet_sales_reason ADD CONSTRAINT fk_fact_internet_sales_reason_sales_reason FOREIGN KEY (sales_reason_key) REFERENCES [SCHEMA].dim_sales_reason (sales_reason_key);