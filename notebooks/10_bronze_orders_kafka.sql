-- Databricks notebook source
-- MAGIC %python
-- MAGIC bootstrap_server = dbutils.secrets.get(
-- MAGIC     "kafka_scope",
-- MAGIC     "confluent_bootstrap_server"
-- MAGIC )
-- MAGIC
-- MAGIC api_key = dbutils.secrets.get(
-- MAGIC     "kafka_scope",
-- MAGIC     "confluent_api_key"
-- MAGIC )
-- MAGIC
-- MAGIC api_secret = dbutils.secrets.get(
-- MAGIC     "kafka_scope",
-- MAGIC     "confluent_api_secret"
-- MAGIC )

-- COMMAND ----------

-- MAGIC %python
-- MAGIC from pyspark.sql.functions import from_json, col, current_timestamp
-- MAGIC from pyspark.sql.types import StructType, StructField, StringType, DoubleType
-- MAGIC
-- MAGIC order_schema = StructType([
-- MAGIC     StructField("order_id", StringType(), True),
-- MAGIC     StructField("customer_id", StringType(), True),
-- MAGIC     StructField("order_ts", StringType(), True),
-- MAGIC     StructField("total_amount", DoubleType(), True),
-- MAGIC     StructField("status", StringType(), True),
-- MAGIC     StructField("channel", StringType(), True)
-- MAGIC ])
-- MAGIC
-- MAGIC kafka_df = (
-- MAGIC     spark.readStream
-- MAGIC     .format("kafka")
-- MAGIC     .option("kafka.bootstrap.servers", bootstrap_server)
-- MAGIC     .option("subscribe", "orders")
-- MAGIC     .option("startingOffsets", "earliest")
-- MAGIC     .option("kafka.security.protocol", "SASL_SSL")
-- MAGIC     .option("kafka.sasl.mechanism", "PLAIN")
-- MAGIC     .option(
-- MAGIC         "kafka.sasl.jaas.config",
-- MAGIC         "kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required "
-- MAGIC         f"username='{api_key}' password='{api_secret}';"
-- MAGIC     )
-- MAGIC     .load()
-- MAGIC )
-- MAGIC
-- MAGIC
-- MAGIC bronze_df = (
-- MAGIC     kafka_df
-- MAGIC     .selectExpr(
-- MAGIC         "CAST(key AS STRING) AS kafka_key",
-- MAGIC         "CAST(value AS STRING) AS raw_json",
-- MAGIC         "topic",
-- MAGIC         "partition",
-- MAGIC         "offset",
-- MAGIC         "timestamp AS kafka_timestamp"
-- MAGIC     )
-- MAGIC     .withColumn("ingested_at", current_timestamp())
-- MAGIC )
-- MAGIC
-- MAGIC query = (
-- MAGIC     bronze_df
-- MAGIC     .writeStream
-- MAGIC     .format("delta")
-- MAGIC     .outputMode("append")
-- MAGIC     .option("checkpointLocation", "/Volumes/workspace/default/proj/checkpoints/orders_kafka_bronze")
-- MAGIC     .trigger(availableNow=True)
-- MAGIC     .toTable("workspace.default.bronze_orders_kafka")
-- MAGIC )
-- MAGIC
-- MAGIC query.awaitTermination()
-- MAGIC

-- COMMAND ----------

SELECT *
FROM workspace.default.bronze_orders_kafka
ORDER BY offset;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC print(query.lastProgress)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC