# Databricks notebook source
dbutils.widgets.text("run_id", "")
dbutils.widgets.text("run_date", "")
dbutils.widgets.text("environment", "dev")

run_id = dbutils.widgets.get("run_id")
run_date = dbutils.widgets.get("run_date")
environment = dbutils.widgets.get("environment")

# COMMAND ----------

from pyspark.sql.functions import current_timestamp
from pyspark.sql import Row

# COMMAND ----------

tables = [
    "bronze_customers",
    "bronze_orders",
    "bronze_order_items",
    "bronze_payments",
    "bronze_products",
    "bronze_support_tickets",
    "bronze_customer_events",
    "silver_customers",
    "silver_orders",
    "silver_order_items",
    "silver_payments",
    "silver_products",
    "silver_support_tickets",
    "silver_customer_events",
    "gold_daily_revenue",
    "gold_payment_success_rate",
    "gold_customer_lifetime_value",
    "gold_product_performance",
    "gold_support_sla_metrics",
    "gold_clickstream_funnel",
    "gold_customer_360",
    "bronze_orders_autoloader",
    "silver_orders_autoloader",
    "gold_daily_revenue_autoloader"
]

# COMMAND ----------

rows = []

for table_name in tables:
    df = spark.table(table_name)

    rows.append(Row(
        run_id=run_id,
        run_date=run_date,
        environment=environment,
        table_name=table_name,
        row_count=df.count()
    ))

audit_df = spark.createDataFrame(rows).withColumn("logged_at", current_timestamp())

audit_df.write.format("delta").mode("overwrite").saveAsTable("pipeline_audit_log")

display(audit_df)

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM pipeline_audit_log ORDER BY logged_at DESC;
# MAGIC