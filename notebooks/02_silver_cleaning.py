# Databricks notebook source
dbutils.widgets.text("run_id", "")
dbutils.widgets.text("run_date", "")
dbutils.widgets.text("environment", "dev")

run_id = dbutils.widgets.get("run_id")
run_date = dbutils.widgets.get("run_date")
environment = dbutils.widgets.get("environment")

# COMMAND ----------

from pyspark.sql.functions import col, to_timestamp, to_date, current_timestamp, lower, trim, try_to_timestamp, expr
from delta.tables import DeltaTable

# COMMAND ----------

bronze_customers = spark.table("bronze_customers")
silver_customers = (bronze_customers.dropDuplicates(["customer_id"])
    .filter(col("customer_id").isNotNull())
    .withColumn("customer_id", trim(col("customer_id")))
    .withColumn("customer_name", trim(col("customer_name")))
    .withColumn("email", lower(trim(col("email"))))
    .withColumn("country", trim(col("country")))
    .withColumn("signup_date", to_date(col("signup_date")))
    .withColumn("customer_segment", lower(trim(col("customer_segment"))))
    .withColumn("marketing_opt_in", col("marketing_opt_in").cast("boolean"))
    .withColumn("processed_at", current_timestamp())
)

if spark.catalog.tableExists("silver_customers"):
    target = DeltaTable.forName(spark, "silver_customers")

    (
        target.alias("target")
        .merge(
            silver_customers.alias("source"),
            "target.customer_id = source.customer_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    silver_customers.write.format("delta").mode("overwrite").saveAsTable("silver_customers")


# COMMAND ----------

bronze_products = spark.table("bronze_products")
silver_products = (bronze_products.dropDuplicates(["product_id"])
    .filter(col("product_id").isNotNull())
    .withColumn("product_id", trim(col("product_id")))
    .withColumn("product_name", trim(col("product_name")))
    .withColumn("category", lower(trim(col("category"))))
    .withColumn("unit_price", col("unit_price").cast("double"))
    .withColumn("active", col("active").cast("boolean"))
    .filter(col("unit_price") > 0)
    .withColumn("processed_at", current_timestamp())
)

if spark.catalog.tableExists("silver_products"):
    target = DeltaTable.forName(spark, "silver_products")

    (
        target.alias("target")
        .merge(
            silver_products.alias("source"),
            "target.product_id = source.product_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    silver_products.write.format("delta").mode("overwrite").saveAsTable("silver_products")
silver_products.show()

# COMMAND ----------

bronze_orders = spark.table("bronze_orders")
silver_orders = (bronze_orders.dropDuplicates(["order_id"])
    .filter(col("order_id").isNotNull())
    .filter(col("customer_id").isNotNull())
    .withColumn("order_id", trim(col("order_id")))
    .withColumn("customer_id", trim(col("customer_id")))
    .withColumn("order_ts", to_timestamp(col("order_ts")))
    .withColumn("status", lower(trim(col("status"))))
    .withColumn("channel", lower(trim(col("channel"))))
    .withColumn("currency", trim(col("currency")))
    .withColumn("total_amount", col("total_amount").cast("double"))
    .filter(col("total_amount") > 0)
    .withColumn("processed_at", current_timestamp())
)

if spark.catalog.tableExists("silver_orders"):
    target = DeltaTable.forName(spark, "silver_orders")

    (
        target.alias("target")
        .merge(
            silver_orders.alias("source"),
            "target.order_id = source.order_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    silver_orders.write.format("delta").mode("overwrite").saveAsTable("silver_orders")

# COMMAND ----------

bronze_order_items = spark.table("bronze_order_items")

silver_order_items = (bronze_order_items.dropDuplicates(["order_id", "product_id"])
    .filter(col("order_id").isNotNull())
    .filter(col("product_id").isNotNull())
    .withColumn("order_id", trim(col("order_id")))
    .withColumn("product_id", trim(col("product_id")))
    .withColumn("quantity", col("quantity").cast("int"))
    .withColumn("unit_price", col("unit_price").cast("double"))
    .withColumn("line_amount", col("line_amount").cast("double"))
    .filter(col("quantity") > 0)
    .filter(col("unit_price") > 0)
    .filter(col("line_amount") > 0)
    .withColumn("proccessed_at", current_timestamp())
)

silver_order_items_deduped = silver_order_items.dropDuplicates(["order_id", "product_id"])

if spark.catalog.tableExists("silver_order_items"):
    target = DeltaTable.forName(spark, "silver_order_items")

    (
        target.alias("target")
        .merge(
            silver_order_items_deduped.alias("source"),
            "target.order_id = source.order_id AND target.product_id = source.product_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    silver_order_items_deduped.write.format("delta").mode("overwrite").saveAsTable("silver_order_items")

# COMMAND ----------

bronze_payments = spark.table("bronze_payments")

silver_payments = (
    bronze_payments
    .dropDuplicates(["payment_id"])
    .filter(col("payment_id").isNotNull())
    .filter(col("order_id").isNotNull())
    .withColumn("payment_id", trim(col("payment_id")))
    .withColumn("order_id", trim(col("order_id")))
    .withColumn("payment_ts", to_timestamp(col("payment_ts")))
    .withColumn("payment_method", lower(trim(col("payment_method"))))
    .withColumn("payment_status", lower(trim(col("payment_status"))))
    .withColumn("amount", col("amount").cast("double"))
    .withColumn("currency", trim(col("currency")))
    .filter(col("amount") > 0)
    .withColumn("processed_at", current_timestamp())
)

if spark.catalog.tableExists("silver_payments"):
    target = DeltaTable.forName(spark, "silver_payments")

    (
        target.alias("target")
        .merge(
            silver_payments.alias("source"),
            "target.payment_id = source.payment_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    silver_payments.write.format("delta").mode("overwrite").saveAsTable("silver_payments")

# COMMAND ----------

bronze_tickets = spark.table("bronze_support_tickets")

silver_support_tickets = (
    bronze_tickets
    .dropDuplicates(["ticket_id"])
    .filter(col("ticket_id").isNotNull())
    .filter(col("customer_id").isNotNull())
    .withColumn("ticket_id", trim(col("ticket_id")))
    .withColumn("customer_id", trim(col("customer_id")))
    .withColumn("created_at", to_timestamp(col("created_at")))
    .withColumn("resolved_at", to_timestamp(col("resolved_at")))
    .withColumn("priority", lower(trim(col("priority"))))
    .withColumn("issue_type", lower(trim(col("issue_type"))))
    .withColumn("status", lower(trim(col("status"))))
    .withColumn("satisfaction_score", col("satisfaction_score").cast("int"))
    .withColumn("processed_at", current_timestamp())
)

if spark.catalog.tableExists("silver_support_tickets"):
    target = DeltaTable.forName(spark, "silver_support_tickets")

    (
        target.alias("target")
        .merge(
            silver_support_tickets.alias("source"),
            "target.ticket_id = source.ticket_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    silver_support_tickets.write.format("delta").mode("overwrite").saveAsTable("silver_support_tickets")


# COMMAND ----------

bronze_events = spark.table("bronze_customer_events")

silver_customer_events = (
    bronze_events
    .dropDuplicates(["event_id"])
    .filter(col("event_id").isNotNull())
    .filter(col("customer_id").isNotNull())
    .withColumn("event_id", trim(col("event_id")))
    .withColumn("customer_id", trim(col("customer_id")))
    .withColumn("event_type", lower(trim(col("event_type"))))
    .withColumn("event_ts", to_timestamp(col("event_ts")))
    .withColumn("channel", lower(trim(col("channel"))))
    .withColumn("product_id", trim(col("product_id")))
    .withColumn("processed_at", current_timestamp())
)

if spark.catalog.tableExists("silver_customer_events"):
    target = DeltaTable.forName(spark, "silver_customer_events")

    (
        target.alias("target")
        .merge(
            silver_customer_events.alias("source"),
            "target.event_id = source.event_id"
        )
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
else:
    silver_customer_events.write.format("delta").mode("overwrite").saveAsTable("silver_customer_events")

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'bronze_orders' AS table_name, COUNT(*) AS row_count FROM bronze_orders
# MAGIC UNION ALL
# MAGIC SELECT 'silver_orders' AS table_name, COUNT(*) AS row_count FROM silver_orders
# MAGIC UNION ALL
# MAGIC SELECT 'bronze_payments' AS table_name, COUNT(*) AS row_count FROM bronze_payments
# MAGIC UNION ALL
# MAGIC SELECT 'silver_payments' AS table_name, COUNT(*) AS row_count FROM silver_payments;