-- Databricks notebook source
-- MAGIC %python
-- MAGIC from pyspark.sql.functions import col, to_timestamp, current_timestamp, lower, trim, regexp_replace
-- MAGIC
-- MAGIC bronze_orders = spark.table("bronze_orders_autoloader")
-- MAGIC
-- MAGIC silver_orders = (
-- MAGIC     bronze_orders
-- MAGIC     .dropDuplicates(["order_id"])
-- MAGIC     .filter(col("order_id").isNotNull())
-- MAGIC     .filter(col("customer_id").isNotNull())
-- MAGIC     .withColumn("order_id", trim(col("order_id")))
-- MAGIC     .withColumn("customer_id", trim(col("customer_id")))
-- MAGIC     .withColumn(
-- MAGIC         "order_ts",
-- MAGIC         to_timestamp(
-- MAGIC             regexp_replace(regexp_replace(col("order_ts"), "T", " "), "Z", ""),
-- MAGIC             "yyyy-MM-dd HH:mm:ss"
-- MAGIC         )
-- MAGIC     )
-- MAGIC     .withColumn("status", lower(trim(col("status"))))
-- MAGIC     .withColumn("channel", lower(trim(col("channel"))))
-- MAGIC     .withColumn("currency", trim(col("currency")))
-- MAGIC     .withColumn("total_amount", col("total_amount").cast("double"))
-- MAGIC     .filter(col("total_amount") > 0)
-- MAGIC     .withColumn("processed_at", current_timestamp())
-- MAGIC )
-- MAGIC
-- MAGIC silver_orders.write.format("delta").mode("overwrite").saveAsTable("silver_orders_autoloader")
-- MAGIC
-- MAGIC display(silver_orders)

-- COMMAND ----------

SELECT COUNT(*) AS row_count
FROM silver_orders_autoloader;