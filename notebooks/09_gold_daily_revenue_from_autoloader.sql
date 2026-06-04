-- Databricks notebook source
-- MAGIC %python
-- MAGIC from pyspark.sql.functions import col, to_date, count, countDistinct, sum, avg, round
-- MAGIC
-- MAGIC orders = spark.table("silver_orders_autoloader")
-- MAGIC
-- MAGIC gold_daily_revenue_autoloader = (
-- MAGIC     orders
-- MAGIC     .groupBy(to_date(col("order_ts")).alias("order_date"))
-- MAGIC     .agg(
-- MAGIC         count("*").alias("order_count"),
-- MAGIC         countDistinct("customer_id").alias("unique_customers"),
-- MAGIC         round(sum("total_amount"), 2).alias("daily_revenue"),
-- MAGIC         round(avg("total_amount"), 2).alias("avg_order_value")
-- MAGIC     )
-- MAGIC     .orderBy("order_date")
-- MAGIC )
-- MAGIC
-- MAGIC gold_daily_revenue_autoloader.write.format("delta").mode("overwrite").saveAsTable("gold_daily_revenue_autoloader")
-- MAGIC
-- MAGIC display(gold_daily_revenue_autoloader)

-- COMMAND ----------

SELECT *
FROM gold_daily_revenue_autoloader
ORDER BY order_date;