CREATE SCHEMA IF NOT EXISTS `mgmt599-kyashawilliams-lab2.store_sales_DN_3`
OPTIONS(
  description="DN 3 Store Sales Analysis",
  location="US"
);
SELECT
  COUNT(*) AS row_count,
  MIN(date) AS earliest_date,
  MAX(date) AS latest_date
FROM
  `mgmt599-kyashawilliams-lab2`.store_sales_DN_3.sales_data;
