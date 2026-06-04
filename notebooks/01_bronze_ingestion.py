# Databricks notebook source
dbutils.widgets.text("run_id", "")
dbutils.widgets.text("run_date", "")
dbutils.widgets.text("environment", "dev")

run_id = dbutils.widgets.get("run_id")
run_date = dbutils.widgets.get("run_date")
environment = dbutils.widgets.get("environment")

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit

# COMMAND ----------

raw_path = "/Volumes/workspace/default/proj/databricks_ecommerce_sample_data/data/raw"


customers_df = spark.read.option("header", True).csv(f"{raw_path}/customers.csv")
products_df = spark.read.option("header", True).csv(f"{raw_path}/products.csv")
orders_df = spark.read.option("header", True).csv(f"{raw_path}/orders.csv")
order_items_df = spark.read.option("header", True).csv(f"{raw_path}/order_items.csv")
payments_df = spark.read.option("header", True).csv(f"{raw_path}/payments.csv")
tickets_df = spark.read.option("header", True).csv(f"{raw_path}/support_tickets.csv")
events_df = spark.read.json(f"{raw_path}/customer_events.jsonl")

customers_df = customers_df.withColumn("ingested_at", current_timestamp()).withColumn("batch_id", lit(run_id)).withColumn("run_date", lit(run_date)).withColumn("environment", lit(environment))
products_df = products_df.withColumn("ingested_at", current_timestamp()).withColumn("batch_id", lit(run_id)).withColumn("run_date", lit(run_date)).withColumn("environment", lit(environment))
orders_df = orders_df.withColumn("ingested_at", current_timestamp()).withColumn("batch_id", lit(run_id)).withColumn("run_date", lit(run_date)).withColumn("environment", lit(environment))
order_items_df = order_items_df.withColumn("ingested_at", current_timestamp()).withColumn("batch_id", lit(run_id)).withColumn("run_date", lit(run_date)).withColumn("environment", lit(environment))
payments_df = payments_df.withColumn("ingested_at", current_timestamp()).withColumn("batch_id", lit(run_id)).withColumn("run_date", lit(run_date)).withColumn("environment", lit(environment))
tickets_df = tickets_df.withColumn("ingested_at", current_timestamp()).withColumn("batch_id", lit(run_id)).withColumn("run_date", lit(run_date)).withColumn("environment", lit(environment))
events_df = events_df.withColumn("ingested_at", current_timestamp()).withColumn("batch_id", lit(run_id)).withColumn("run_date", lit(run_date)).withColumn("environment", lit(environment))

customers_df.write.format("delta").mode("append").saveAsTable("bronze_customers")
products_df.write.format("delta").mode("append").saveAsTable("bronze_products")
orders_df.write.format("delta").mode("append").saveAsTable("bronze_orders")
order_items_df.write.format("delta").mode("append").saveAsTable("bronze_order_items")
payments_df.write.format("delta").mode("append").saveAsTable("bronze_payments")
tickets_df.write.format("delta").mode("append").saveAsTable("bronze_support_tickets")
events_df.write.format("delta").mode("append").saveAsTable("bronze_customer_events")
