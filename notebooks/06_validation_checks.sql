-- Databricks notebook source
-- MAGIC %python
-- MAGIC dbutils.widgets.text("run_id", "")
-- MAGIC dbutils.widgets.text("run_date", "")
-- MAGIC dbutils.widgets.text("environment", "dev")
-- MAGIC
-- MAGIC run_id = dbutils.widgets.get("run_id")
-- MAGIC run_date = dbutils.widgets.get("run_date")
-- MAGIC environment = dbutils.widgets.get("environment")

-- COMMAND ----------

    SHOW TABLES;

-- COMMAND ----------

SELECT *
FROM data_quality_results
ORDER BY checked_at DESC
LIMIT 50;

-- COMMAND ----------

SELECT *
FROM bronze_orders
LIMIT 10;

-- COMMAND ----------

SELECT batch_id, run_date, environment, COUNT(*) AS row_count
FROM bronze_orders
GROUP BY batch_id, run_date, environment
ORDER BY batch_id;

-- COMMAND ----------

SELECT batch_id, run_date, environment, COUNT(*) AS row_count
FROM bronze_orders
GROUP BY batch_id, run_date, environment
ORDER BY batch_id;

-- COMMAND ----------

SELECT 'bronze_orders' AS table_name, COUNT(*) AS row_count FROM bronze_orders
UNION ALL
SELECT 'silver_orders' AS table_name, COUNT(*) AS row_count FROM silver_orders;

-- COMMAND ----------

SELECT *
FROM bronze_orders_autoloader
ORDER BY order_id;

-- COMMAND ----------

SELECT *
FROM silver_orders_autoloader
ORDER BY order_id;

-- COMMAND ----------

SELECT *
FROM gold_daily_revenue_autoloader
ORDER BY order_date;

-- COMMAND ----------

SELECT *
FROM data_quality_results
WHERE table_name = 'silver_orders_autoloader'
ORDER BY checked_at DESC;

-- COMMAND ----------

SELECT *
FROM pipeline_audit_log
WHERE table_name LIKE '%autoloader%'
ORDER BY logged_at DESC;