CREATE SCHEMA IF NOT EXISTS gold;
CREATE SCHEMA IF NOT EXISTS rag;
CREATE TABLE gold.dim_date (date_key int PRIMARY KEY, full_date date, year
int, quarter int, month int,
month_name text, day_of_month int, day_of_week int, is_weekend boolean);
CREATE TABLE gold.dim_customer (customer_key bigint PRIMARY KEY, customer_id
bigint, age_group text);
CREATE TABLE gold.dim_product (product_key bigint PRIMARY KEY, product_id
bigint, product_name text, category text);
CREATE TABLE gold.dim_store (store_key bigint PRIMARY KEY, store_id bigint,
store_name text);
CREATE TABLE gold.dim_geography (geography_key bigint PRIMARY KEY, department
text, city text);
CREATE TABLE gold.fact_sales (order_item_id bigint, order_id bigint, date_key
int, customer_key bigint,
product_key bigint, store_key bigint, geography_key bigint, order_date
date, quantity int,
discount_pct double precision, unit_price numeric(14,2), gross_amount
numeric(14,2),
discount_amount numeric(14,2), net_amount numeric(14,2), order_status text,
payment_method text);
