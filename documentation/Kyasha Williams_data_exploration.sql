SELECT * FROM `mgmt599-kyashawilliams-lab2.assignment2_storesales.stores` LIMIT 1000;
SELECT
  COUNT(DISTINCT store_nbr)
FROM
  `mgmt599-kyashawilliams-lab2`.assignment2_storesales.stores;
SELECT
  MIN(date) AS start_date,
  MAX(date) AS end_date
FROM
  `mgmt599-kyashawilliams-lab2`.assignment2_storesales.train;
SELECT
    DISTINCT family
FROM
    `mgmt599-kyashawilliams-lab2.assignment2_storesales.train`
ORDER BY
    family;
