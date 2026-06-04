-- Databricks notebook source
-- MAGIC %python
-- MAGIC from pyspark.sql.functions import current_timestamp, lit
-- MAGIC from datetime import date
-- MAGIC import uuid
-- MAGIC
-- MAGIC source_path = "/Volumes/workspace/default/proj/databricks_ecommerce_sample_data/data/raw_autoloader/orders"
-- MAGIC schema_path = "/Volumes/workspace/default/proj/schemas/autoloader/bronze_orders"
-- MAGIC checkpoint_path = "/Volumes/workspace/default/proj/checkpoints/autoloader/bronze_orders"
-- MAGIC
-- MAGIC run_id = str(uuid.uuid4())
-- MAGIC run_date = str(date.today())
-- MAGIC environment = "dev"
-- MAGIC
-- MAGIC orders_stream = (
-- MAGIC     spark.readStream
-- MAGIC         .format("cloudFiles")
-- MAGIC         .option("cloudFiles.format", "csv")
-- MAGIC         .option("header", "true")
-- MAGIC         .option("cloudFiles.schemaLocation", schema_path)
-- MAGIC         .load(source_path)
-- MAGIC         .withColumn("ingested_at", current_timestamp())
-- MAGIC         .withColumn("batch_id", lit(run_id))
-- MAGIC         .withColumn("run_date", lit(run_date))
-- MAGIC         .withColumn("environment", lit(environment))
-- MAGIC )
-- MAGIC
-- MAGIC query = (
-- MAGIC     orders_stream.writeStream
-- MAGIC         .format("delta")
-- MAGIC         .outputMode("append")
-- MAGIC         .option("checkpointLocation", checkpoint_path)
-- MAGIC         .trigger(availableNow=True)
-- MAGIC         .toTable("bronze_orders_autoloader")
-- MAGIC )

-- COMMAND ----------

DESCRIBE bronze_orders_autoloader;

-- COMMAND ----------

select count(*) from bronze_orders_autoloader